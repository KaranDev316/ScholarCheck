import { isPassedRound } from '../data/funding'
import type { RoundView } from '../data/types'

interface DateRoundTableProps {
  rounds: readonly RoundView[]
}

function displayRoundStatus(round: RoundView): string {
  if (isPassedRound(round) && round.status === 'Deadline published') return 'Date passed'
  if (round.status === 'Confirm with provider') return 'Check with institution'
  if (round.status === 'Not published') return 'Not announced'
  return round.status
}

export function DateRoundTable({ rounds }: DateRoundTableProps) {
  return (
    <>
      <div className="table-wrap tblwrap">
        <table className="round-table tbl">
          <thead>
            <tr>
              <th scope="col">Round</th>
              <th scope="col">Date</th>
              <th scope="col">Status</th>
              <th scope="col">Note</th>
            </tr>
          </thead>
          <tbody>
            {rounds.map((round) => (
              <tr key={round.id}>
                <td>{round.round}</td>
                <td>{round.dateAsPublished}</td>
                <td>
                  <span className="tag">{displayRoundStatus(round)}</span>
                </td>
                <td className="muted small">{round.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="small muted">
        A passed date marks that round only. Other rounds stay as they are until a source says
        otherwise.
      </p>
    </>
  )
}
