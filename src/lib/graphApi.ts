// ── Graph API Types ─────────────────────────────────────────────────────

export interface GraphSeriesRaw {
  label: string;
  color: string;
  fillOpacity: number;
  data: number[];
}

export interface GraphApiResponse {
  title: string;
  xLabels: string[]; // one label per data point
  series: GraphSeriesRaw[];
}

// ── Mock datasets ───────────────────────────────────────────────────────

const MOCK_DATASETS: Record<string, GraphApiResponse> = {
  default: {
    title: "Strategy vs Benchmark.",
    xLabels: [
      "Jun 20", "Jul 20", "Aug 20", "Sep 20", "Oct 20", "Nov 20",
      "Dec 20", "Jan 21", "Feb 21", "Mar 21", "Apr 21", "May 21",
      "Jun 21", "Jul 21", "Aug 21", "Sep 21", "Oct 21", "Nov 21",
      "Dec 21", "Jan 22", "Feb 22", "Mar 22", "Apr 22", "May 22",
      "Jun 22", "Jul 22", "Aug 22", "Sep 22", "Oct 22", "Nov 22",
      "Dec 22", "Jan 23", "Feb 23", "Mar 23", "Apr 23", "May 23",
      "Jun 23", "Jul 23", "Aug 23", "Sep 23", "Oct 23", "Nov 23",
    ],
    series: [
      {
        label: "Strategy",
        color: "#d4d4d4",
        fillOpacity: 1,
        data: [
          0, 5, -8, 15, 10, 25, 18, 55, 35, 80, 45, 30,
          20, 50, 38, 25, 15, 10, 18, 30, 22, 15, 55, 40,
          65, 20, 38, 50, 35, 80, 110, 60, 95, 75, 130, 105,
          85, 140, 120, 100, 15, 10,
        ],
      },
      {
        label: "Benchmark",
        color: "#707070",
        fillOpacity: 0,
        data: [
          5, 8, 10, 12, 15, 14, 16, 18, 15, 20, 18, 14,
          16, 15, 12, 18, 16, 14, 15, 18, 16, 14, 12, 15,
          18, 16, 14, 15, 18, 16, 14, 15, 18, 16, 14, 15,
          18, 16, 15, 14, 12, 15,
        ],
      },
    ],
  },
  drawdown: {
    title: "Drawdown.",
    xLabels: [
      "Jun 20", "Jul 20", "Aug 20", "Sep 20", "Oct 20", "Nov 20",
      "Dec 20", "Jan 21", "Feb 21", "Mar 21", "Apr 21", "May 21",
      "Jun 21", "Jul 21", "Aug 21", "Sep 21", "Oct 21", "Nov 21",
      "Dec 21", "Jan 22", "Feb 22", "Mar 22", "Apr 22", "May 22",
      "Jun 22", "Jul 22", "Aug 22", "Sep 22", "Oct 22", "Nov 22",
      "Dec 22", "Jan 23", "Feb 23", "Mar 23", "Apr 23", "May 23",
      "Jun 23", "Jul 23", "Aug 23", "Sep 23",
    ],
    series: [
      {
        label: "Main",
        color: "#d4d4d4",
        fillOpacity: 1,
        data: [
          55, 50, 58, 65, 72, 60, 85, 95, 78, 65, 88, 72,
          60, 55, 75, 82, 68, 58, 62, 70, 55, 80, 90, 72,
          95, 105, 85, 78, 110, 95, 130, 105, 120, 115, 140, 125,
          110, 135, 128, 120,
        ],
      },
      {
        label: "Secondary",
        color: "#707070",
        fillOpacity: 0,
        data: [
          0, -10, 5, -15, -5, 10, -8, 15, -20, 8, -12, 5,
          -18, 10, -5, -15, 8, -10, 5, -20, 10, -8, -25, 5,
          -15, 10, -30, 5, -10, 15, -20, 8, -12, 5, -25, 10,
          -8, -15, 5, -10,
        ],
      },
    ],
  },
  momentum: {
    title: "Dual Momentum Returns.",
    xLabels: [
      "Q1 21", "Q2 21", "Q3 21", "Q4 21",
      "Q1 22", "Q2 22", "Q3 22", "Q4 22",
      "Q1 23", "Q2 23", "Q3 23", "Q4 23",
      "Q1 24", "Q2 24", "Q3 24", "Q4 24",
      "Q1 25", "Q2 25",
    ],
    series: [
      {
        label: "Dual Momentum",
        color: "#d4d4d4",
        fillOpacity: 1,
        data: [
          12, 18, 8, 25, 32, 15, -5, 10, 22, 38, 42, 55,
          48, 62, 58, 72, 85, 78,
        ],
      },
      {
        label: "S&P 500",
        color: "#707070",
        fillOpacity: 0,
        data: [
          10, 14, 12, 18, 15, 8, -2, 5, 12, 20, 25, 30,
          28, 35, 32, 40, 45, 42,
        ],
      },
    ],
  },
};

// ── Mock fetch (simulates network delay) ────────────────────────────────

export async function fetchGraphData(query?: string): Promise<GraphApiResponse[]> {
  // Simulate network latency
  await new Promise((r) => setTimeout(r, 1200 + Math.random() * 800));

  // Simple keyword matching to pick datasets
  const q = (query ?? "").toLowerCase();
  if (q.includes("drawdown")) return [MOCK_DATASETS.drawdown];
  if (q.includes("momentum")) return [MOCK_DATASETS.momentum];
  if (q.includes("all")) return [MOCK_DATASETS.default, MOCK_DATASETS.drawdown];

  // Default: return strategy vs benchmark
  return [MOCK_DATASETS.default];
}
