import { useState, useRef } from 'react';
import { uploadApi } from '@/api/upload';
import { Upload as UploadIcon, Camera, CheckCircle, AlertCircle, Trash2, Edit2, Check, X } from 'lucide-react';

interface ExtractedRow {
  name: string;
  phone: string;
  visit_date: string | null;
  next_visit_date: string | null;
}

interface ReviewRow extends ExtractedRow {
  _id: number;
  _editing: boolean;
  _included: boolean;
}

type Stage = 'idle' | 'uploading' | 'review' | 'confirming' | 'done' | 'error';

export default function Upload() {
  const [stage, setStage] = useState<Stage>('idle');
  const [uploadType, setUploadType] = useState<'excel' | 'photo'>('excel');
  const [dragActive, setDragActive] = useState(false);

  // Photo review state
  const [uploadId, setUploadId] = useState('');
  const [reviewRows, setReviewRows] = useState<ReviewRow[]>([]);
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
    setStage('uploading');

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
          setStage('error');
          return;
        }

        if (data.status === 'already_processed') {
          setResult({ ...data, total_rows: data.total_extracted, new_patients: data.total_extracted });
          setStage('done');
          return;
        }

        // Pending review — show the review table
        setUploadId(data.upload_id);
        setProvider(data.provider || 'nvidia');
        setExtractionErrors(data.errors || []);
        setReviewRows(
          (data.extracted_rows || []).map((row: ExtractedRow, i: number) => ({
            ...row,
            _id: i,
            _editing: false,
            _included: true,
          }))
        );
        setStage('review');
      }
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Upload failed');
      setStage('error');
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
    const confirmed = reviewRows.filter(r => r._included).map(r => ({
      name: r.name,
      phone: r.phone,
      visit_date: r.visit_date || null,
      next_visit_date: r.next_visit_date || null,
    }));

    setStage('confirming');
    try {
      const res = await uploadApi.confirmPhoto({ upload_id: uploadId, confirmed_rows: confirmed });
      setResult(res.data);
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
    setUploadId('');
    if (fileRef.current) fileRef.current.value = '';
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  };

  const includedCount = reviewRows.filter(r => r._included).length;

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-800">Upload</h1>
        <p className="text-sm text-slate-500 mt-0.5">Upload Excel sheets or photos of your patient register</p>
      </div>

      {/* Type Toggle — only when idle or after reset */}
      {(stage === 'idle' || stage === 'error') && (
        <div className="flex gap-2">
          {(['excel', 'photo'] as const).map((type) => (
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

      {/* Drop Zone */}
      {(stage === 'idle' || stage === 'error') && (
        <div
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={(e) => { e.preventDefault(); setDragActive(false); if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]); }}
          onClick={() => fileRef.current?.click()}
          className={`cursor-pointer border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive ? 'border-slate-400 bg-slate-50' : 'border-slate-200 hover:border-slate-300'
          }`}
        >
          <input
            ref={fileRef}
            type="file"
            accept={uploadType === 'excel' ? '.xlsx,.xls' : 'image/*'}
            onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
            className="hidden"
          />
          {uploadType === 'excel'
            ? <UploadIcon className="w-8 h-8 text-slate-300 mx-auto mb-3" />
            : <Camera className="w-8 h-8 text-slate-300 mx-auto mb-3" />
          }
          <p className="text-sm text-slate-600">
            Drop your {uploadType === 'excel' ? '.xlsx file' : 'photo'} here, or{' '}
            <span className="text-slate-900 font-medium">browse</span>
          </p>
          <p className="text-xs text-slate-400 mt-1">{uploadType === 'excel' ? 'Max 10 MB' : 'Max 20 MB'}</p>
        </div>
      )}

      {/* Uploading spinner */}
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
            <button onClick={reset} className="text-xs text-slate-400 hover:text-slate-600">
              Cancel
            </button>
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
                    <th className="px-3 py-2 text-left text-xs font-medium text-slate-500">Next Visit</th>
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

                      {/* Visit date */}
                      <td className="px-3 py-2 text-xs text-slate-500">
                        {row.visit_date || '—'}
                      </td>

                      {/* Next visit */}
                      <td className="px-3 py-2 text-xs text-slate-500">
                        {row.next_visit_date || '—'}
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
          <div className="flex items-center justify-between pt-1">
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
                disabled={includedCount === 0}
                className="px-4 py-1.5 text-sm bg-slate-900 text-white rounded-lg hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Save {includedCount} Patient{includedCount !== 1 ? 's' : ''}
              </button>
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
