// AC2: dashboard api module tests (REQ-ARCH-032 frontend half, t20).
//
// Seven frozen nodes (docs/issues/t20.md inventory). Each node resolves an
// endpoint against a `server.use` fixture that copies the merged t19 wire
// shape VERBATIM (dashboard_service.py lines 213-220 / 266-273 / 314 /
// 352-355 / 402-407) and asserts the FROZEN key set — no extra key, no
// missing key. handlers.ts and setup.ts stay byte-identical (t16 ruling),
// so every handler here is a per-test override that ALSO records the
// request URL and the bearer header: the header proves the calls travel
// through the SHARED client interceptor (never raw axios), and the recorded
// query params pin `year_month` AT THE HANDLER rather than by code reading.

import { beforeEach, describe, expect, it } from 'vitest';
import { http, HttpResponse } from 'msw';
import { demoExpense } from '../test/handlers';
import { server } from '../test/server';
import {
  getByCategory,
  getCumulative,
  getHeatmap,
  getRecent,
  getSummary,
  getTrend
} from './dashboard';
import { TOKEN_KEY } from './client';

interface SeenRequest {
  /** Parsed request URL (path + query params are asserted from it). */
  url: URL;
  /** Authorization header the SHARED client interceptor attached. */
  auth: string;
}

/** Requests seen by the registered fixtures, in arrival order. */
const seen: SeenRequest[] = [];

/** Register a recording fixture for one dashboard path echoing its body. */
const fixture = (path: string, body: Record<string, unknown>): void => {
  server.use(
    http.get(path, ({ request }) => {
      seen.push({
        url: new URL(request.url),
        auth: request.headers.get('Authorization') ?? ''
      });
      return HttpResponse.json(body, { status: 200 });
    })
  );
};

/** Frozen t19 summary body (money strings, percentage a JSON number). */
const summaryBody = {
  year_month: '2026-02',
  total: '125.50',
  budget_amount: '2000.00',
  remaining: '1874.50',
  percentage: 6.3,
  is_over_budget: false,
  category_count: 2
};

/** Frozen t19 by-category body: rows carry exactly five keys. */
const byCategoryBody = {
  year_month: '2026-02',
  total: '125.50',
  categories: [
    {
      category_id: demoExpense.category_id,
      category_name: demoExpense.category_name,
      color: demoExpense.category_color,
      amount: '125.50',
      percentage: 100.0
    }
  ]
};

/** Frozen t19 trend body: items carry EXACTLY two keys, no label. */
const trendBody = {
  months: [
    { year_month: '2026-01', total: '0.00' },
    { year_month: '2026-02', total: '125.50' }
  ]
};

/** Frozen t19 cumulative body: day rows carry exactly three keys. */
const cumulativeBody = {
  year_month: '2026-02',
  budget: '2000.00',
  days: [
    { date: '2026-02-01', daily: '0.00', cumulative: '0.00' },
    { date: '2026-02-03', daily: '125.50', cumulative: '125.50' }
  ]
};

/** Frozen t19 heatmap body: Monday week starts, seven days per week. */
const heatmapBody = {
  max_amount: '125.50',
  weeks: [
    {
      week_start: '2026-01-05',
      days: [
        { date: '2026-01-05', amount: '0.00' },
        { date: '2026-01-06', amount: '0.00' },
        { date: '2026-01-07', amount: '0.00' },
        { date: '2026-01-08', amount: '0.00' },
        { date: '2026-01-09', amount: '0.00' },
        { date: '2026-01-10', amount: '0.00' },
        { date: '2026-01-11', amount: '0.00' }
      ]
    },
    {
      week_start: '2026-01-12',
      days: [
        { date: '2026-01-12', amount: '0.00' },
        { date: '2026-01-13', amount: '0.00' },
        { date: '2026-01-14', amount: '0.00' },
        { date: '2026-01-15', amount: '0.00' },
        { date: '2026-01-16', amount: '0.00' },
        { date: '2026-01-17', amount: '0.00' },
        { date: '2026-01-18', amount: '125.50' }
      ]
    }
  ]
};

/** Recent items reuse the merged ten-key expense shape. */
const recentBody = { items: [demoExpense] };

beforeEach(() => {
  seen.length = 0;
  // The shared client's request interceptor reads this key (REQ-ARCH-042);
  // its presence is asserted at the handler as shared-client evidence.
  window.localStorage.setItem(TOKEN_KEY, 'test-token-abc');
});

describe('dashboard api (ac2)', () => {
  it('the summary call resolves the seven frozen keys through the shared client', async () => {
    fixture('/api/v1/dashboard/summary', summaryBody);
    const data = await getSummary('2026-02');
    expect(Object.keys(data).sort()).toEqual([
      'budget_amount',
      'category_count',
      'is_over_budget',
      'percentage',
      'remaining',
      'total',
      'year_month'
    ]);
    // Money stays a string; percentage stays the JSON number (no coercion).
    expect(data.total).toBe('125.50');
    expect(data.budget_amount).toBe('2000.00');
    expect(data.remaining).toBe('1874.50');
    expect(typeof data.percentage).toBe('number');
    // Shared-client proof, observed AT THE HANDLER: the request carried the
    // bearer header that api/client.ts's interceptor attaches, so the call
    // travelled through the shared instance and not a private axios call.
    expect(seen).toHaveLength(1);
    expect(seen[0]?.auth).toBe('Bearer test-token-abc');
  });

  it('getSummary sends the year_month query param', async () => {
    fixture('/api/v1/dashboard/summary', summaryBody);
    await getSummary('2026-02');
    expect(seen).toHaveLength(1);
    const url = seen[0];
    expect(url?.url.pathname).toBe('/api/v1/dashboard/summary');
    // Pinned AT THE HANDLER: the driving month travels as year_month.
    expect(url?.url.searchParams.get('year_month')).toBe('2026-02');
  });

  it('the by-category rows carry the five frozen keys with string amounts', async () => {
    fixture('/api/v1/dashboard/by-category', byCategoryBody);
    const data = await getByCategory('2026-02');
    expect(Object.keys(data).sort()).toEqual(['categories', 'total', 'year_month']);
    const row = data.categories[0];
    expect(Object.keys(row ?? {}).sort()).toEqual([
      'amount',
      'category_id',
      'category_name',
      'color',
      'percentage'
    ]);
    expect(typeof row?.amount).toBe('string');
    expect(typeof row?.percentage).toBe('number');
    const url = seen[0];
    expect(url?.url.searchParams.get('year_month')).toBe('2026-02');
  });

  it('the trend items carry exactly the year_month and total keys', async () => {
    fixture('/api/v1/dashboard/trend', trendBody);
    const data = await getTrend(2);
    expect(Object.keys(data)).toEqual(['months']);
    for (const item of data.months) {
      // Exactly two keys: NO label key (the merged shape).
      expect(Object.keys(item).sort()).toEqual(['total', 'year_month']);
      expect(typeof item.total).toBe('string');
    }
    const url = seen[0];
    expect(url?.url.searchParams.get('months')).toBe('2');
  });

  it('the cumulative day rows carry the date daily and cumulative keys', async () => {
    fixture('/api/v1/dashboard/cumulative', cumulativeBody);
    const data = await getCumulative('2026-02');
    expect(Object.keys(data).sort()).toEqual(['budget', 'days', 'year_month']);
    for (const day of data.days) {
      expect(Object.keys(day).sort()).toEqual(['cumulative', 'daily', 'date']);
      expect(typeof day.daily).toBe('string');
      expect(typeof day.cumulative).toBe('string');
    }
    const url = seen[0];
    expect(url?.url.searchParams.get('year_month')).toBe('2026-02');
  });

  it('the heatmap weeks carry seven Monday-start days and the max amount', async () => {
    fixture('/api/v1/dashboard/heatmap', heatmapBody);
    const data = await getHeatmap(2);
    expect(Object.keys(data).sort()).toEqual(['max_amount', 'weeks']);
    expect(data.max_amount).toBe('125.50');
    expect(data.weeks).toHaveLength(2);
    for (const week of data.weeks) {
      expect(Object.keys(week).sort()).toEqual(['days', 'week_start']);
      expect(week.days).toHaveLength(7);
      // Monday start: getUTCDay() === 1 for every week_start.
      const start = Date.parse(`${week.week_start}T00:00:00Z`);
      expect(new Date(start).getUTCDay()).toBe(1);
      // The seven days are the seven consecutive days from week_start.
      week.days.forEach((day, index) => {
        const expected = new Date(start + index * 86_400_000).toISOString().slice(0, 10);
        expect(day.date).toBe(expected);
        expect(Object.keys(day).sort()).toEqual(['amount', 'date']);
      });
    }
    const url = seen[0];
    expect(url?.url.searchParams.get('weeks')).toBe('2');
  });

  it('the recent items reuse the ten-key expense shape', async () => {
    fixture('/api/v1/dashboard/recent', recentBody);
    const data = await getRecent(5);
    expect(Object.keys(data)).toEqual(['items']);
    const item = data.items[0];
    expect(Object.keys(item ?? {}).sort()).toEqual([
      'amount',
      'category_color',
      'category_id',
      'category_name',
      'created_at',
      'currency',
      'date',
      'id',
      'note',
      'updated_at'
    ]);
    expect(typeof item?.amount).toBe('string');
    const url = seen[0];
    expect(url?.url.searchParams.get('limit')).toBe('5');
  });
});
