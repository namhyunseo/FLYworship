// Vercel Serverless Function
// 찬양의 밤 추천곡 신청 건수(= 신청한 사람 수)만 세어 돌려줍니다.
// 개별 신청 내용(추천곡·사연·이름)은 노출하지 않고, 총 개수만 반환합니다.
//
// 필요한 환경변수: worship-request.js와 동일
//   NOTION_TOKEN, NOTION_DATA_SOURCE_ID

const NOTION_VERSION = '2025-09-03';

export default async function handler(req, res) {
    if (req.method !== 'GET') {
        res.setHeader('Allow', 'GET');
        return res.status(405).json({ error: 'Method Not Allowed' });
    }

    const token = process.env.NOTION_TOKEN;
    const dataSourceId = process.env.NOTION_DATA_SOURCE_ID;
    if (!token || !dataSourceId) {
        console.error('환경변수 누락: NOTION_TOKEN 또는 NOTION_DATA_SOURCE_ID');
        return res.status(500).json({ error: '서버 설정 오류' });
    }

    try {
        let count = 0;
        let cursor = undefined;

        // 데이터소스를 페이지네이션하며 개수만 누적 (내용은 무시)
        do {
            const r = await fetch(
                `https://api.notion.com/v1/data_sources/${dataSourceId}/query`,
                {
                    method: 'POST',
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Notion-Version': NOTION_VERSION,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        page_size: 100,
                        start_cursor: cursor,
                    }),
                }
            );

            if (!r.ok) {
                const detail = await r.text();
                console.error('Notion API 오류', r.status, detail);
                return res.status(502).json({ error: '집계에 실패했습니다.' });
            }

            const data = await r.json();
            count += Array.isArray(data.results) ? data.results.length : 0;
            cursor = data.has_more ? data.next_cursor : undefined;
        } while (cursor);

        // CDN에서 30초간 캐시 → Notion 호출 최소화 (방문자가 많아도 안전)
        res.setHeader('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=120');
        return res.status(200).json({ count });
    } catch (err) {
        console.error('요청 실패', err);
        return res.status(502).json({ error: '집계에 실패했습니다.' });
    }
}
