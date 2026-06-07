// Vercel Serverless Function
// 찬양의 밤 추천곡 신청을 Notion 데이터소스에 저장합니다. (Notion 2025-09-03 API)
//
// 필요한 환경변수 (Vercel 프로젝트 Settings → Environment Variables):
//   NOTION_TOKEN            : Notion 통합(Integration) 토큰
//   NOTION_DATA_SOURCE_ID   : 저장할 데이터소스 ID
//
// 데이터소스 속성(컬럼): 추천 찬양(제목), 아티스트, 이름, 방향(선택), 사연, 제출일시(생성시간 자동)

const NOTION_VERSION = '2025-09-03';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        res.setHeader('Allow', 'POST');
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const token = process.env.NOTION_TOKEN;
    const dataSourceId = process.env.NOTION_DATA_SOURCE_ID;
    if (!token || !dataSourceId) {
        console.error('환경변수 누락: NOTION_TOKEN 또는 NOTION_DATA_SOURCE_ID');
        return res.status(500).json({ error: '서버 설정 오류' });
    }

    let body = req.body;
    if (typeof body === 'string') {
        try { body = JSON.parse(body); } catch { body = {}; }
    }
    body = body || {};

    // 허니팟: 봇이 채우는 숨김 필드. 값이 있으면 조용히 성공 처리(스팸 차단).
    if (body.website) return res.status(200).json({ ok: true });

    const name = String(body.name || '').trim().slice(0, 100);
    const songTitle = String(body.songTitle || '').trim().slice(0, 200);
    const songArtist = String(body.songArtist || '').trim().slice(0, 200);
    const songMood = String(body.songMood || '').trim().slice(0, 20);
    const story = String(body.story || '').trim().slice(0, 420);

    if (!songTitle || !story) {
        return res.status(400).json({ error: '추천 찬양과 사연은 필수입니다.' });
    }

    const properties = {
        '추천 찬양': { title: [{ text: { content: songTitle } }] },
        '사연': { rich_text: [{ text: { content: story } }] },
    };
    if (songArtist) properties['아티스트'] = { rich_text: [{ text: { content: songArtist } }] };
    if (name) properties['이름'] = { rich_text: [{ text: { content: name } }] };
    if (songMood) properties['방향'] = { select: { name: songMood } };

    try {
        const r = await fetch('https://api.notion.com/v1/pages', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
                'Notion-Version': NOTION_VERSION,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                parent: { type: 'data_source_id', data_source_id: dataSourceId },
                properties,
            }),
        });

        if (!r.ok) {
            const detail = await r.text();
            console.error('Notion API 오류', r.status, detail);
            return res.status(502).json({ error: '저장에 실패했습니다. 잠시 후 다시 시도해 주세요.' });
        }

        return res.status(200).json({ ok: true });
    } catch (err) {
        console.error('요청 실패', err);
        return res.status(502).json({ error: '저장에 실패했습니다. 잠시 후 다시 시도해 주세요.' });
    }
}
