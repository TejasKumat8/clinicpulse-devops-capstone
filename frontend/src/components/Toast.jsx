import { useEffect } from 'react';

export default function Toast({ message, tone, onDone }) {
  useEffect(() => {
    const timer = setTimeout(onDone, 3500);
    return () => clearTimeout(timer);
  }, [onDone]);

  return (
    <div className={`toast toast-${tone}`} role="status" aria-live="polite">
      <span aria-hidden>{tone === 'error' ? '⚠' : '✓'}</span> {message}
    </div>
  );
}
