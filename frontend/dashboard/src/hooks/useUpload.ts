import { useState } from 'react';

export function useUpload() {
  const [uploading, setUploading] = useState(false);
  return { uploading, upload: () => {} };
}
