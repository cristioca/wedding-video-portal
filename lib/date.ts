export function daysRemaining(dateStr: string | Date) {
  const target = new Date(dateStr);
  const now = new Date();
  const diff = Math.ceil((target.getTime() - now.getTime()) / (1000*60*60*24));
  return diff < 0 ? 0 : diff;
}
