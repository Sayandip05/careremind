import { useState, useRef } from 'react';
import { uploadApi } from '@/api/upload';
import { useGuestMode } from '@/context/GuestModeContext';
import { Upload as UploadIcon, Camera, CheckCircle, AlertCircle, Trash2, Check } from 'lucide-react';

interface ExtractedRow {
  name: string;
  phone: string;
  visit_date: string | null;
  next_visit_date: string | null;
}

interface ReviewRow extends ExtractedRow {
  _id: number;
  _uploadId: string;
  _editing: boolean;
  _included: boolean;
}

type Stage = 'idle' | 'uploading' | 'review' | 'confirming' | 'done' | 'error';

export default function Upload() {
  const { isGuest, requireAuth } = useGuestMode();
  const [stage, setStage] = useState<Stage>('idle');
  const [uploadType, setUploadType] = useState<'excel' | 'photo'>('photo');
  const [dragActive, setDragActive] = useState(false);
  // True when a new photo is being processed while rows are already in the table
  const [isAddingMore, setIsAddingMore] = useState(false);

  // Photo review state

  const [reviewRows, setReviewRows] = useState<ReviewRow[]>([]);
  const [bulkDate, setBulkDate] = useState('');
  const [extractionErrors, setExtractionErrors] = useState<string[]>([]);
  const [provider, setProvider] = useState('');

  // Final result
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const fileRef = useRef<HTMLInputElement>(null);

  // ── File handling ──────────────────────────────────────────────────────────

  const handleFile = async (file: File) => {
    setErrorMsg('');
    setResult(null);

    // If rows already exist in the table, keep the review stage visible
    // and just show a subtle inline spinner — don't wipe the table.
    const addingToExisting = stage === 'review' && reviewRows.length > 0;
    if (addingToExisting) {
      setIsAddingMore(true);
    } else {
      setStage('uploading');
    }

    try {
      if (uploadType === 'excel') {
        const res = await uploadApi.uploadExcel(file);
        setResult(res.data);
        setStage(res.data.status === 'failed' ? 'error' : 'done');
        if (res.data.status === 'failed' && res.data.errors?.length) {
          setErrorMsg(res.data.errors.join(' • '));
        }
      } else {
        // Photo: extract only — don't save yet
        const res = await uploadApi.uploadPhoto(file);
        const data = res.data;

        if (data.status === 'failed') {
          setErrorMsg(data.errors?.join(' • ') || 'Image processing failed');
          if (!addingToExisting) setStage('error');
          return;
        }

        if (data.status === 'already_processed') {
          // If adding to existing table, just skip silently with a note
          if (addingToExisting) {
            setExtractionErrors(prev => [...prev, 'One photo was already processed — skipped duplicate.']);
          } else {
            setResult({ ...data, total_rows: data.total_extracted, new_patients: data.total_extracted });
            setStage('done');
          }
          return;
        }

        // Pending review — append rows to the table
        setProvider(data.provider || 'nvidia');
        setExtractionErrors(prev => [...prev, ...(data.errors || [])]);

        // Apply the current bulkDate to new rows if one is already set
        const newRows = (data.extracted_rows || []).map((row: ExtractedRow, i: number) => ({
          ...row,
          _id: Date.now() + i,
          _uploadId: data.upload_id,
          _editing: false,
          _included: true,
          // Pre-fill visit_date from bulkDate if the AI didn't find one
          visit_date: row.visit_date || bulkDate || null,
        }));

        setReviewRows(prev => [...prev, ...newRows]);
        setStage('review');
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Upload failed');
      if (!addingToExisting) setStage('error');
    } finally {
      setIsAddingMore(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  // ── Review table actions ───────────────────────────────────────────────────

  const toggleRow = (id: number) =>
    setReviewRows(rows => rows.map(r => r._id === id ? { ...r, _included: !r._included } : r));

  const deleteRow = (id: number) =>
    setReviewRows(rows => rows.filter(r => r._id !== id));

  const updateRow = (id: number, field: keyof ExtractedRow, value: string) =>
    setReviewRows(rows => rows.map(r => r._id === id ? { ...r, [field]: value } : r));

  const handleConfirm = async () => {
    const includedRows = reviewRows.filter(r => r._included);

    // Hard validation — every included patient must have a visit date
    const missingDate = includedRows.filter(r => !r.visit_date);
    if (missingDate.length > 0) {
      setErrorMsg(
        `${missingDate.length} patient${missingDate.length > 1 ? 's are' : ' is'} missing a visit date. Please fill in the date before saving.`
      );
      return;
    }
    
    // Group confirmed rows by upload ID
    const groupedByUpload: Record<string, any[]> = {};
    for (const r of includedRows) {
      if (!groupedByUpload[r._uploadId]) groupedByUpload[r._uploadId] = [];
      groupedByUpload[r._uploadId].push({
        name: r.name,
        phone: r.phone,
        visit_date: r.visit_date || null,
        next_visit_date: null, // Removed from UI
      });
    }

    setStage('confirming');
    try {
      const promises = Object.entries(groupedByUpload).map(([uid, rows]) => 
        uploadApi.confirmPhoto({ upload_id: uid, confirmed_rows: rows })
      );
      
      const responses = await Promise.all(promises);
      
      // Aggregate results from multiple uploads
      const aggregated = responses.reduce((acc, res) => {
        const d = res.data;
        return {
          status: 'completed',
          total_rows: (acc.total_rows || 0) + (d.total_rows || 0),
          new_patients: (acc.new_patients || 0) + (d.new_patients || 0),
          duplicates: (acc.duplicates || 0) + (d.duplicates || 0),
          skipped: (acc.skipped || 0) + (d.skipped || 0),
          errors: [...(acc.errors || []), ...(d.errors || [])],
        };
      }, { total_rows: 0, new_patients: 0, duplicates: 0, skipped: 0, errors: [] });

      setResult(aggregated);
      setStage('done');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Save failed');
      setStage('error');
    }
  };

  const reset = () => {
    setStage('idle');
    setResult(null);
    setErrorMsg('');
    setReviewRows([]);
    setBulkDate('');
    setExtractionErrors([]);
    setIsAddingMore(false);
    if (fileRef.current) fileRef.current.value = '';
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const includedCount = reviewRows.filter(r => r._included).length;
  const missingDateCount = reviewRows.filter(r => r._included && !r.visit_date).length;

  // ── Render ─────────────────────────────────────────────────────────────────

  // Guest preview: show the upload UI but intercept any file interaction
  const handleGuestDrop = (e: React.DragEvent) => {
    e.preventDefault();
    requireAuth();
  };

  return (
    <div className="space-y-6 pt-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Upload</h1>
        <p className="text-sm text-slate-500 mt-0.5">Upload Excel sheets or photos of your patient register</p>
      </div>

      {/* Type Toggle — only when idle or after reset */}
      {(stage === 'idle' || stage === 'error') && (
        <div className="flex gap-2">
          {(['photo', 'excel'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setUploadType(type)}
              className={`flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                uploadType === type
                  ? 'bg-slate-900 text-white'
                  : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {type === 'excel' ? <UploadIcon className="w-4 h-4" /> : <Camera className="w-4 h-4" />}
              {type === 'excel' ? 'Excel' : 'Photo'}
            </button>
          ))}
        </div>
      )}

      {/* Drop Zone — shown when idle, on error, or in review (to add more photos) */}
      {(stage === 'idle' || stage === 'error' || stage === 'review') && (
        <div
          onDragEnter={isGuest ? (e) => { e.preventDefault(); } : handleDrag}
          onDragOver={isGuest ? (e) => { e.preventDefault(); } : handleDrag}
          onDragLeave={isGuest ? (e) => { e.preventDefault(); } : handleDrag}
          onDrop={isGuest ? handleGuestDrop : (e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]); }}
          onClick={() => {
            if (isGuest) { requireAuth(); return; }
            if (!isAddingMore) fileRef.current?.click();
          }}
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isAddingMore
              ? 'border-slate-200 bg-slate-50 cursor-not-allowed opacity-60'
              : dragActive
                ? 'border-slate-400 bg-slate-50 cursor-pointer'
                : 'border-slate-200 hover:border-slate-300 cursor-pointer'
          }`}
        >
          <input
            ref={fileRef}
            type="file"
            accept={uploadType === 'excel' ? '.xlsx,.xls' : 'image/*'}
            onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
            className="hidden"
            disabled={isAddingMore}
          />
          {isAddingMore ? (
            <>
              <div className="w-6 h-6 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin mx-auto mb-2" />
              <p className="text-sm text-slate-500">AI is extracting from new photo…</p>
              <p className="text-xs text-slate-400 mt-1">Your existing patients are safe above</p>
            </>
          ) : (
            <>
              {uploadType === 'excel'
                ? <UploadIcon className="w-8 h-8 text-slate-300 mx-auto mb-3" />
                : <Camera className="w-8 h-8 text-slate-300 mx-auto mb-3" />
              }
              <p className="text-sm text-slate-600">
                Drop your {uploadType === 'excel' ? '.xlsx file' : 'photo'} here, or{' '}
                <span className="text-slate-900 font-medium">browse</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {uploadType === 'excel' ? 'Max 10 MB' : (stage === 'review' ? 'Max 20 MB • Add more pages to the list above' : 'Max 20 MB')}
              </p>
            </>
          )}
        </div>
      )}

      {/* Full-page uploading spinner — only shown when no rows exist yet */}
      {stage === 'uploading' && (
        <div className="border border-slate-200 rounded-lg p-10 text-center">
          <div className="w-7 h-7 border-2 border-slate-200 border-t-slate-700 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-600">
            {uploadType === 'photo' ? 'Running AI vision extraction…' : 'Processing file…'}
          </p>
          {uploadType === 'photo' && (
            <p className="text-xs text-slate-400 mt-1">Using NVIDIA {provider || 'llama-3.2-11b-vision-instruct'}</p>
          )}
        </div>
      )}

      {/* Confirming spinner */}
      {stage === 'confirming' && (
        <div className="border border-slate-200 rounded-lg p-10 text-center">
          <div className="w-7 h-7 border-2 border-slate-200 border-t-slate-700 rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-slate-600">Saving {includedCount} patient{includedCount !== 1 ? 's' : ''}…</p>
        </div>
      )}

      {/* Error message */}
      {(stage === 'error' || errorMsg) && (
        <div className="flex items-start gap-2 text-sm text-red-700 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{errorMsg || 'An error occurred'}</span>
        </div>
      )}

      {/* ── REVIEW STAGE (Human-in-the-Loop) ── */}
      {stage === 'review' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-800">
                Review Extracted Patients
                <span className="ml-2 text-xs font-normal text-slate-400">
                  (via {provider})
                </span>
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                AI found {reviewRows.length} patient{reviewRows.length !== 1 ? 's' : ''}.
                Review, edit, or remove rows before saving.
              </p>
            </div>
            <div className="flex items-center gap-4">
              {reviewRows.length > 0 && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="text-slate-500">Set date for all:</span>
                  <input
                    type="date"
                    className="border border-slate-200 rounded px-2 py-1 text-slate-700 bg-white"
                    value={bulkDate}
                    onChange={(e) => {
                      const d = e.target.value;
                      setBulkDate(d);
                      setReviewRows(rows => rows.map(r => ({ ...r, visit_date: d })));
                    }}
                  />
                </div>
              )}
              <button onClick={reset} className="text-xs text-slate-400 hover:text-slate-600">
                Cancel
              </button>
            </div>
          </div>

          {extractionErrors.length > 0 && (
            <div className="text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded px-3 py-2">
              {extractionErrors.join(' • ')}
            </div>
          )}

          {reviewRows.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-sm border border-slate-200 rounded-lg">
              No patients were extracted from this image.
              <br />
              <button onClick={reset} className="mt-2 text-slate-600 underline text-xs">Upload a different photo</button>
            </div>
          ) : (
            <div className="border border-slate-200 rounded-lg overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 w-8"></th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-slate-500">Name</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-slate-500">Phone</th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-slate-500">Visit Date</th>
                    <th className="px-3 py-2 w-8"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {reviewRows.map((row) => (
                    <tr
                      key={row._id}
                      className={`transition-colors ${row._included ? '' : 'opacity-40 bg-slate-50'}`}
                    >
                      {/* Include toggle */}
                      <td className="px-3 py-2">
                        <button
                          onClick={() => toggleRow(row._id)}
                          className={`w-4 h-4 rounded border flex items-center justify-center ${
                            row._included
                              ? 'bg-slate-900 border-slate-900 text-white'
                              : 'border-slate-300'
                          }`}
                        >
                          {row._included && <Check className="w-3 h-3" />}
                        </button>
                      </td>

                      {/* Name */}
                      <td className="px-3 py-2">
                        <input
                          className="w-full bg-transparent outline-none text-slate-800 focus:bg-slate-50 rounded px-1"
                          value={row.name}
                          onChange={(e) => updateRow(row._id, 'name', e.target.value)}
                          disabled={!row._included}
                        />
                      </td>

                      {/* Phone */}
                      <td className="px-3 py-2">
                        <input
                          className="w-full bg-transparent outline-none text-slate-600 font-mono text-xs focus:bg-slate-50 rounded px-1"
                          value={row.phone}
                          onChange={(e) => updateRow(row._id, 'phone', e.target.value)}
                          disabled={!row._included}
                        />
                      </td>

                      {/* Visit date — required, highlighted red if missing */}
                      <td className="px-3 py-2 text-xs">
                        <input
                          type="date"
                          className={`w-full bg-transparent outline-none rounded px-1 ${
                            row._included && !row.visit_date
                              ? 'border border-red-300 bg-red-50 text-red-700 placeholder-red-300'
                              : 'text-slate-600 focus:bg-slate-50'
                          }`}
                          value={row.visit_date || ''}
                          onChange={(e) => updateRow(row._id, 'visit_date', e.target.value)}
                          disabled={!row._included}
                        />
                      </td>

                      {/* Delete */}
                      <td className="px-3 py-2">
                        <button
                          onClick={() => deleteRow(row._id)}
                          className="text-slate-300 hover:text-red-500 transition-colors"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Confirm bar */}
          <div className="space-y-2 pt-1">
            {missingDateCount > 0 && (
              <div className="flex items-center gap-2 text-xs text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>
                  <strong>{missingDateCount} patient{missingDateCount > 1 ? 's' : ''}</strong> {missingDateCount > 1 ? 'are' : 'is'} missing a visit date — use "Set date for all" above or fill individually.
                </span>
              </div>
            )}
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-400">
                {includedCount} of {reviewRows.length} rows selected
              </p>
              <div className="flex gap-2">
                <button
                  onClick={reset}
                  className="px-3 py-1.5 text-sm border border-slate-200 rounded-lg text-slate-600 hover:bg-slate-50"
                >
                  Discard
                </button>
                <button
                  onClick={handleConfirm}
                  disabled={includedCount === 0 || missingDateCount > 0}
                  className="px-4 py-1.5 text-sm bg-slate-900 text-white rounded-lg hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Save {includedCount} Patient{includedCount !== 1 ? 's' : ''}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── DONE — Final result ── */}
      {stage === 'done' && result && (
        <div className="bg-white border border-slate-200 rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-slate-700">
                {result.status === 'already_processed' ? 'Already uploaded' : 'Saved successfully'}
              </span>
            </div>
            <button onClick={reset} className="text-xs text-slate-400 hover:text-slate-600">
              Upload another
            </button>
          </div>
          <div className="grid grid-cols-4 gap-4">
            {[
              { label: 'Total Rows', value: result.total_rows ?? result.total_extracted ?? 0 },
              { label: 'New Patients', value: result.new_patients ?? 0 },
              { label: 'Duplicates', value: result.duplicates ?? 0 },
              { label: 'Skipped', value: result.skipped ?? 0 },
            ].map((item) => (
              <div key={item.label} className="text-center">
                <p className="text-xl font-semibold text-slate-800">{item.value}</p>
                <p className="text-xs text-slate-500">{item.label}</p>
              </div>
            ))}
          </div>
          {result.errors?.length > 0 && (
            <div className="mt-3 text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded px-3 py-2">
              {result.errors.join(' • ')}
            </div>
          )}
          {result.note && (
            <p className="mt-2 text-xs text-slate-400">{result.note}</p>
          )}
        </div>
      )}
    </div>
  );
}
