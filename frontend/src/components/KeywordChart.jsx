import ChartWrapper from './ui/ChartWrapper'

function KeywordRow({ word, count, maxCount }) {
  const pct = maxCount > 0 ? (count / maxCount) * 100 : 0
  return (
    <div className="keyword-row">
      <span className="keyword-row__word">{word}</span>
      <div className="keyword-row__bar-wrap">
        <div className="keyword-row__bar" style={{ width: `${pct}%` }} />
      </div>
      <span className="keyword-row__count">{count}</span>
    </div>
  )
}

export default function KeywordChart({ data = [], loading = false, error = null }) {
  const maxCount = data.length > 0 ? data[0].count : 1

  return (
    <ChartWrapper
      loading={loading}
      error={error}
      empty={!data.length}
      height={320}
      emptyTitle="No keywords yet"
      emptyMessage="Keyword intelligence will appear after data collection."
    >
      <div className="keyword-list">
        {data.slice(0, 20).map((item) => (
          <KeywordRow
            key={item.word}
            word={item.word}
            count={item.count}
            maxCount={maxCount}
          />
        ))}
      </div>
    </ChartWrapper>
  )
}
