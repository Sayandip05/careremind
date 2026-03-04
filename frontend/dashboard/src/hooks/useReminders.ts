import { useState } from 'react';

export function useReminders() {
  const [reminders, setReminders] = useState([]);
  return { reminders, fetchReminders: () => {} };
}
