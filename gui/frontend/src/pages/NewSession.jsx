import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Play, Upload } from 'lucide-react';
import apiClient from '../services/api';
import { Layout, ShellBadge } from '../components/Layout';

const defaultForm = {
  inventory_file: '',
  target_firmware_version: '',
  execution_mode: 'sequential',
  notes: '',
};

export const NewSession = () => {
  const navigate = useNavigate();
  const [form, setForm] = useState(defaultForm);
  const [inventoryFiles, setInventoryFiles] = useState([]);
  const [firmwareVersions, setFirmwareVersions] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [startAfterCreate, setStartAfterCreate] = useState(false);

  const loadOptions = useCallback(async () => {
    try {
      setLoading(true);
      const [inventoryRes, firmwareRes] = await Promise.all([
        apiClient.getInventoryFiles(),
        apiClient.getFirmwareVersions(),
      ]);
      const inventories = inventoryRes.data.inventory_files || [];
      const versions = firmwareRes.data.firmware_versions || [];
      setInventoryFiles(inventories);
      setFirmwareVersions(versions);
      setForm((current) => ({
        ...current,
        inventory_file: current.inventory_file || inventories[0] || '',
        target_firmware_version: current.target_firmware_version || versions[0] || '',
      }));
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Nem sikerült betölteni a beállításokat.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOptions();
  }, [loadOptions]);

  const canSubmit = useMemo(
    () => form.inventory_file && form.target_firmware_version && !submitting,
    [form.inventory_file, form.target_firmware_version, submitting]
  );

  const updateField = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const uploadInventory = async () => {
    if (!uploadFile) {
      setUploadMessage('Válassz egy .yml vagy .yaml fájlt.');
      return;
    }

    try {
      setUploading(true);
      setError('');
      setUploadMessage('');

      const response = await apiClient.uploadInventoryFile(uploadFile);
      const uploadedInventory = response.data.inventory_file;

      await loadOptions();
      setForm((current) => ({
        ...current,
        inventory_file: uploadedInventory,
      }));
      setUploadMessage(`Feltöltve: ${response.data.original_filename}`);
      setUploadFile(null);
    } catch (err) {
      setUploadMessage('');
      setError(err?.response?.data?.detail || err.message || 'Nem sikerült feltölteni az inventory fájlt.');
    } finally {
      setUploading(false);
    }
  };

  const formatInventoryLabel = (file) => {
    const isUploaded = file.startsWith('/data/inventory-uploads');
    const name = file.split('/').filter(Boolean).pop() || file;
    if (isUploaded) {
      return `${name} · uploaded`;
    }
    return file;
  };

  const submit = async (event) => {
    event.preventDefault();
    try {
      setSubmitting(true);
      setError('');

      const response = await apiClient.createSession({
        inventory_file: form.inventory_file,
        target_firmware_version: form.target_firmware_version,
        execution_mode: form.execution_mode,
        notes: form.notes || undefined,
      });

      const sessionId = response.data.session_id;
      if (startAfterCreate) {
        await apiClient.startSession(sessionId);
      }

      navigate(`/jobs/${sessionId}`);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Nem sikerült létrehozni a jobot.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Layout
      title="New job"
      subtitle="Upload or choose an inventory file, then create a job for the upgrade flow."
      backTo="/"
      actions={<ShellBadge>{loading ? 'loading options' : 'ready'}</ShellBadge>}
    >
      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.9fr]">
        <form onSubmit={submit} className="space-y-5 rounded-3xl border border-white/8 bg-white/5 p-6">
          {error && (
            <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
              {error}
            </div>
          )}

          <div className="rounded-3xl border border-cyan-400/15 bg-cyan-400/5 p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-cyan-200">Inventory upload</div>
                <p className="mt-1 text-sm text-slate-400">
                  Upload a new YAML inventory, or choose an existing one from the list below.
                </p>
              </div>
              <ShellBadge>{uploading ? 'uploading' : 'local file'}</ShellBadge>
            </div>

            <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
              <label className="block">
                <span className="sr-only">Inventory file to upload</span>
                <input
                  type="file"
                  accept=".yml,.yaml"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-cyan-500 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-slate-950 hover:file:bg-cyan-400"
                />
              </label>

              <button
                type="button"
                onClick={uploadInventory}
                disabled={uploading || !uploadFile}
                className="inline-flex items-center justify-center gap-2 rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-4 py-3 text-sm font-semibold text-cyan-200 transition hover:bg-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {uploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
                Upload inventory
              </button>
            </div>

            {uploadMessage && (
              <div className="mt-3 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200">
                {uploadMessage}
              </div>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-300">Inventory file</span>
              <select
                value={form.inventory_file}
                onChange={(e) => updateField('inventory_file', e.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400/40"
              >
                {inventoryFiles.length === 0 && <option value="">No inventory files found</option>}
                {inventoryFiles.map((file) => (
                  <option key={file} value={file}>
                    {formatInventoryLabel(file)}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-300">Target version</span>
              <select
                value={form.target_firmware_version}
                onChange={(e) => updateField('target_firmware_version', e.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400/40"
              >
                {firmwareVersions.length === 0 && <option value="">No versions found</option>}
                {firmwareVersions.map((version) => (
                  <option key={version} value={version}>
                    {version}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-300">Execution mode</span>
              <select
                value={form.execution_mode}
                onChange={(e) => updateField('execution_mode', e.target.value)}
                className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400/40"
              >
                <option value="sequential">Sequential</option>
                <option value="parallel">Parallel</option>
              </select>
            </label>

            <label className="space-y-2">
              <span className="text-sm font-medium text-slate-300">Action</span>
              <label className="flex h-[52px] items-center gap-3 rounded-2xl border border-white/10 bg-slate-950/60 px-4 text-sm text-slate-200">
                <input
                  type="checkbox"
                  checked={startAfterCreate}
                  onChange={(e) => setStartAfterCreate(e.target.checked)}
                  className="h-4 w-4 rounded border-white/20 bg-transparent text-cyan-400"
                />
                Create and start immediately
              </label>
            </label>
          </div>

          <label className="space-y-2 block">
            <span className="text-sm font-medium text-slate-300">Notes</span>
            <textarea
              value={form.notes}
              onChange={(e) => updateField('notes', e.target.value)}
              rows={5}
              placeholder="Optional operational notes, change window or approval reference."
              className="w-full rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400/40"
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              disabled={!canSubmit}
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {submitting ? <Loader2 className="animate-spin" size={18} /> : <Play size={18} />}
              {submitting ? 'Creating...' : 'Create job'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="rounded-xl border border-white/10 px-5 py-3 text-sm font-semibold text-slate-300 transition hover:border-white/20 hover:text-white"
            >
              Cancel
            </button>
          </div>
        </form>

        <div className="space-y-4">
          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <h2 className="text-lg font-semibold text-white">How this MVP works</h2>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-400">
              <li>1. Upload a YAML inventory or choose an existing one.</li>
              <li>2. The job tracks progress and audit events.</li>
              <li>3. Start and resume stay on the job page.</li>
              <li>4. Rollback is handled from an individual firewall detail view.</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-white/8 bg-white/5 p-6">
            <h2 className="text-lg font-semibold text-white">Available inputs</h2>
            <div className="mt-4 space-y-2 text-sm text-slate-400">
              <div>Inventory files: {inventoryFiles.length || 0}</div>
              <div>Firmware versions: {firmwareVersions.length || 0}</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};
