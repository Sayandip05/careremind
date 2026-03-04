import { useState } from 'react';

export function usePatients() {
  const [patients, setPatients] = useState([]);
  return { patients, fetchPatients: () => {} };
}
