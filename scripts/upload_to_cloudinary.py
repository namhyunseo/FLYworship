#!/usr/bin/env python3
"""
oikos share 사진 → Cloudinary 벌크 업로드 + photos.json 매니페스트 생성 (1회성 도구)

- .env.local 에서 Cloudinary 키를 읽는다 (키를 코드에 박지 않는다).
- 소스 폴더를 재귀 순회해 이미지(.jpg/.jpeg/.png)만 올린다. 영상(.mp4 등)·csv는 건너뛴다.
- 조별 서브폴더 이름이 파일명 충돌을 막아준다 → public_id = oikos-2026/<조>/<파일명>.
- overwrite=False 라서 재실행/중단 후 재개해도 이미 올라간 건 그냥 건너뛴다(멱등).
- 업로드 응답에서 가로/세로(w/h)를 모아 archives/2026/oikos-gallery/photos.json 로 쓴다.

실행:  .venv-tools/bin/python scripts/upload_to_cloudinary.py "/경로/오이코스셰어-사진 2"
"""

import os
import re
import sys
import json
import concurrent.futures as futures

import cloudinary
import cloudinary.uploader

# ── 경로 설정 ──────────────────────────────────────────────
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(REPO, ".env.local")
MANIFEST_PATH = os.path.join(REPO, "archives", "2026", "oikos-gallery", "photos.json")
CLOUD_FOLDER = "oikos-2026"          # Cloudinary 안에서 사진이 모일 폴더
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
WORKERS = 8                          # 동시 업로드 개수


def load_env(path):
    """.env.local 의 KEY=VALUE 를 dict 로 (따옴표/공백 정리)."""
    env = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def safe_group(name):
    """조 폴더 이름을 URL-safe ASCII 로. (한글은 매핑 후 나머지는 _ 로 치환)"""
    name = name.replace("그룹", "group").replace("미지정", "unassigned")
    name = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    return name or "etc"


def day_rank(stem):
    """파일명 접두사로 시간순 정렬 키. PRE < DAY1 < DAY2 < DAY3 < 기타."""
    order = {"PRE": 0, "DAY1": 1, "DAY2": 2, "DAY3": 3}
    m = re.match(r"(PRE|DAY\d+)", stem.upper())
    return order.get(m.group(1), 9) if m else 9


def seq_num(stem):
    """파일명 끝 번호 (없으면 0)."""
    m = re.search(r"(\d+)\D*$", stem)
    return int(m.group(1)) if m else 0


def collect_images(src):
    """(로컬경로, public_id, 조, 파일명stem) 목록. 조별 서브폴더 1단계 기준."""
    items = []
    for root, _dirs, files in os.walk(src):
        group = safe_group(os.path.basename(root)) if root != src else "root"
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in IMAGE_EXTS:
                continue
            stem = os.path.splitext(fn)[0]
            public_id = f"{CLOUD_FOLDER}/{group}/{stem}"
            items.append((os.path.join(root, fn), public_id, group, stem))
    return items


def upload_one(item):
    path, public_id, group, stem = item
    res = cloudinary.uploader.upload(
        path,
        public_id=public_id,
        overwrite=False,        # 이미 있으면 재업로드 안 함(멱등)
        resource_type="image",
        unique_filename=False,
        use_filename=False,
    )
    return {
        "id": public_id,
        "w": res["width"],
        "h": res["height"],
        "day": re.match(r"(PRE|DAY\d+)", stem.upper()).group(1)
        if re.match(r"(PRE|DAY\d+)", stem.upper()) else "ETC",
        "_stem": stem,
        "_group": group,
    }


def main():
    if len(sys.argv) < 2:
        sys.exit("사용법: python scripts/upload_to_cloudinary.py <사진폴더경로>")
    src = sys.argv[1]
    if not os.path.isdir(src):
        sys.exit(f"폴더 없음: {src}")

    env = load_env(ENV_PATH)
    cloud = env.get("CLOUDINARY_CLOUD_NAME", "")
    key = env.get("CLOUDINARY_API_KEY", "")
    secret = env.get("CLOUDINARY_API_SECRET", "")
    if not (cloud and key and secret):
        sys.exit("`.env.local` 에 CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET 셋 다 필요")

    cloudinary.config(cloud_name=cloud, api_key=key, api_secret=secret, secure=True)

    items = collect_images(src)
    total = len(items)
    print(f"이미지 {total}개 발견 → Cloudinary '{CLOUD_FOLDER}' 로 업로드 시작")

    results, done, failed = [], 0, []
    with futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        fut2item = {ex.submit(upload_one, it): it for it in items}
        for fut in futures.as_completed(fut2item):
            done += 1
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001
                failed.append((fut2item[fut][1], str(e)))
            if done % 25 == 0 or done == total:
                print(f"  {done}/{total} 완료 (실패 {len(failed)})")

    if failed:
        print("\n⚠️ 실패한 업로드:")
        for pid, err in failed[:20]:
            print(f"  - {pid}: {err}")
        print("  (다시 실행하면 성공한 건 건너뛰고 실패분만 재시도됨)")

    # 시간순 정렬: day → 조 → 번호
    results.sort(key=lambda r: (day_rank(r["_stem"]), r["_group"], seq_num(r["_stem"])))
    photos = [{"id": r["id"], "w": r["w"], "h": r["h"], "day": r["day"]} for r in results]

    manifest = {"cloud_name": cloud, "folder": CLOUD_FOLDER, "count": len(photos), "photos": photos}
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    print(f"\n✅ 매니페스트 저장: {os.path.relpath(MANIFEST_PATH, REPO)} ({len(photos)}장)")
    if failed:
        print("   실패분이 있으니 스크립트를 한 번 더 실행해줘.")


if __name__ == "__main__":
    main()
