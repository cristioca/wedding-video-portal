type Props = { status: "IN_PROGRES"|"IN_ASTEPTARE"|"PARTIAL"|"FINALIZATA"|"Pending" };
export default function StatusBadge({ status }: Props) {
  const map: Record<Props["status"], { label: string, cls: string }> = {
    IN_PROGRES: { label: "În progres", cls: "badge-blue" },
    IN_ASTEPTARE: { label: "În așteptare", cls: "badge-yellow" },
    PARTIAL: { label: "Parțial finalizată", cls: "badge-gray" },
    FINALIZATA: { label: "Finalizată", cls: "badge-green" },
    Pending: { label: "În așteptare", cls: "badge-yellow" },
  };
  const { label, cls } = map[status];
  return <span className={`badge ${cls}`}>{label}</span>;
}
