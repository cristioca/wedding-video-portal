"use client";

import { useState, useEffect } from "react";
import type { Project, File as FileModel } from "@prisma/client";
import StatusBadge from "./StatusBadge";

// The component expects a single project, not an array
type ProjectWithFiles = Project & { files: FileModel[] };

interface Props {
  project: any;
  userRole: string;
  pendingModifications?: any[];
}

export default function ProjectTabs({ project, userRole, pendingModifications = [] }: Props) {
  const [tab, setTab] = useState<"detalii" | "editare" | "filme">("detalii");

  // Use the passed userRole to determine admin status
  const isAdmin = userRole === "ADMIN";

  return (
    <div className="space-y-4">
      <div className="flex gap-2 border-b border-gray-700 pb-2">
        {["detalii", "editare", "filme"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t as any)}
            className={`px-3 py-1 rounded-md text-sm font-medium ${
              tab === t
                ? "bg-white text-black"
                : "bg-transparent text-gray-300 hover:bg-gray-700"
            }`}
          >
            {t === "detalii"
              ? "Detalii"
              : t === "editare"
              ? "Editare video"
              : "Filme"}
          </button>
        ))}
      </div>

      {tab === "detalii" && <DetaliiTab project={project} isAdmin={isAdmin} pendingModifications={pendingModifications} />}
      {tab === "editare" && <EditareTab project={project} />}
      {tab === "filme" && <FilmeTab project={project} isAdmin={isAdmin} />}
    </div>
  );
}

function Field({
  label,
  value,
  editable = false,
  onEdit,
  projectId,
  pendingValue,
  hasPendingChange,
  isAdmin = false,
  modificationId,
  inputType = 'text',
  selectOptions,
}: {
  label: string;
  value?: string | null;
  editable?: boolean;
  onEdit?: () => void;
  projectId: string;
  pendingValue?: string;
  hasPendingChange?: boolean;
  isAdmin?: boolean;
  modificationId?: string;
  inputType?: 'text' | 'date' | 'select';
  selectOptions?: { value: string; label: string }[];
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value || "");

  useEffect(() => {
    setEditValue(value || "");
  }, [value]);

  const handleSave = async () => {
    try {
      const response = await fetch(`/api/projects/${projectId}/update`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field: getFieldName(label),
          value: editValue,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setIsEditing(false);
        if (onEdit) onEdit();
        
        if (result.applied) {
          // Admin change - refresh to show updated data
          window.location.reload();
        } else {
          // Client change - show pending message
          window.location.reload();
        }
      } else {
        console.error('Failed to save field');
      }
    } catch (error) {
      console.error('Error saving field:', error);
    }
  };

  // Helper function to map Romanian labels to field names
  const getFieldName = (label: string): string => {
    const fieldMap: { [key: string]: string } = {
      'Data evenimentului': 'eventDate',
      'Titlu video': 'titleVideo',
      'Oraș': 'city',
      'Căsătorie civilă': 'civilUnionDetails',
      'Pregătiri': 'prep',
      'Biserica': 'church',
      'Sesiune foto-video': 'session',
      'Restaurant': 'restaurant',
      'Alte detalii': 'detailsExtra',
    };
    return fieldMap[label] || label.toLowerCase();
  };

  const handleCancel = () => {
    setEditValue(value || "");
    setIsEditing(false);
  };

  const handleApproveModification = async () => {
    if (!modificationId) return;
    
    try {
      const response = await fetch(`/api/projects/${projectId}/modifications`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          modificationId,
          action: 'approve'
        }),
      });

      if (response.ok) {
        window.location.reload();
      } else {
        alert('Eroare la aprobarea modificării.');
      }
    } catch (error) {
      console.error('Error approving modification:', error);
      alert('Eroare la aprobarea modificării.');
    }
  };

  const handleRejectModification = async () => {
    if (!modificationId) return;
    
    const notes = prompt('Motiv pentru respingere (opțional):');
    
    try {
      const response = await fetch(`/api/projects/${projectId}/modifications`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          modificationId,
          action: 'reject',
          notes
        }),
      });

      if (response.ok) {
        window.location.reload();
      } else {
        alert('Eroare la respingerea modificării.');
      }
    } catch (error) {
      console.error('Error rejecting modification:', error);
      alert('Eroare la respingerea modificării.');
    }
  };

  return (
    <div className="flex items-start justify-between gap-3 py-2 border-b border-[#252a35]">
      <div className="flex-1">
        <div className="text-sm text-gray-400">{label}</div>
        {isEditing ? (
          <div className="mt-1">
            {inputType === 'select' ? (
              <select
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-md px-2 py-1.5 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                autoFocus
              >
                <option value="">Selectează...</option>
                {selectOptions?.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            ) : (
              <input
                type={inputType}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-md px-2 py-1 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                autoFocus
              />
            )}
            <div className="mt-2 flex gap-2">
              <button
                onClick={handleSave}
                className="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 rounded text-xs font-medium"
              >
                Salvează
              </button>
              <button
                onClick={handleCancel}
                className="px-2 py-1 bg-gray-600 hover:bg-gray-700 rounded text-xs font-medium"
              >
                Anulează
              </button>
            </div>
          </div>
        ) : (
          <div>
            {hasPendingChange ? (
              <div>
                <div className="font-medium text-yellow-200">{pendingValue || "-"}</div>
                <div className="text-xs text-gray-500 line-through mt-1">
                  Valoare anterioară: {value || "-"}
                </div>
                <div className="mt-1 p-2 bg-yellow-900/30 border border-yellow-600 rounded text-xs">
                  <div className="text-yellow-400 font-medium">Modificare în așteptare</div>
                  {isAdmin ? (
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={handleApproveModification}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 rounded text-xs font-medium text-white"
                      >
                        Aprobă
                      </button>
                      <button
                        onClick={handleRejectModification}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-xs font-medium text-white"
                      >
                        Respinge
                      </button>
                    </div>
                  ) : (
                    <div className="text-yellow-500 text-xs mt-1">
                      Așteaptă aprobarea de către Videograf
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-between mt-1">
                <div className={`${hasPendingChange ? 'text-yellow-200' : 'text-white'}`}>
                  {value || "-"}
                </div>
                {editable && (
                  <button 
                    onClick={() => setIsEditing(true)}
                    className="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-medium ml-2"
                  >
                    Editează
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function DetaliiTab({ project, isAdmin, pendingModifications }: { project: any; isAdmin: boolean; pendingModifications: any[] }) {
  // Helper function to get pending modification for a field
  const getPendingModification = (fieldName: string) => {
    return pendingModifications.find((mod: any) => 
      mod.fieldName === fieldName && mod.status === 'PENDING'
    );
  };

  const displayedFieldNames = [
    'eventDate', 'titleVideo', 'city', 'civilUnionDetails', 'prep', 
    'church', 'session', 'restaurant', 'detailsExtra'
  ];

  const unmappedModifications = pendingModifications.filter(
    (mod: any) => !displayedFieldNames.includes(mod.fieldName) && mod.status === 'PENDING'
  );

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      {isAdmin && unmappedModifications.length > 0 && (
        <div className="mb-4 p-3 bg-red-900/50 border border-red-700 rounded-lg text-sm">
          <p className="font-bold text-red-400">Atenție: Există {unmappedModifications.length} modificări în așteptare pentru câmpuri care nu pot fi afișate:</p>
          <ul className="list-disc list-inside mt-2 text-red-300">
            {unmappedModifications.map((mod: any) => (
              <li key={mod.id}>
                Câmp: <strong>{mod.fieldName}</strong>, Valoare nouă: "{mod.newValue}"
              </li>
            ))}
          </ul>
          <p className="text-xs text-red-400 mt-2">Acestea pot fi modificări vechi sau corupte. Contactați suportul tehnic dacă nu pot fi rezolvate.</p>
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
        <Field
          label="Data evenimentului"
          value={project.eventDate.toISOString().slice(0, 10)}
          editable
          projectId={project.id}
          pendingValue={getPendingModification('eventDate')?.newValue}
          hasPendingChange={!!getPendingModification('eventDate')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('eventDate')?.id}
          inputType="date"
        />
        <Field
          label="Tip eveniment"
          value={project.type === "NUNTA" ? "nuntă" : "botez"}
          projectId={project.id}
        />
        <Field 
          label="Titlu video" 
          value={project.titleVideo} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('titleVideo')?.newValue}
          hasPendingChange={!!getPendingModification('titleVideo')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('titleVideo')?.id}
        />
        <Field 
          label="Oraș" 
          value={project.city} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('city')?.newValue}
          hasPendingChange={!!getPendingModification('city')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('city')?.id}
        />
        <Field
          label="Căsătorie civilă"
          value={project.civilUnionDetails}
          editable
          projectId={project.id}
          pendingValue={getPendingModification('civilUnionDetails')?.newValue}
          hasPendingChange={!!getPendingModification('civilUnionDetails')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('civilUnionDetails')?.id}
          inputType="select"
          selectOptions={[
            { value: 'Făcută deja', label: 'Făcută deja' },
            { value: 'Aceeași zi', label: 'Aceeași zi' },
          ]}
        />
        <Field 
          label="Pregătiri" 
          value={project.prep} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('prep')?.newValue}
          hasPendingChange={!!getPendingModification('prep')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('prep')?.id}
        />
        <Field 
          label="Biserica" 
          value={project.church} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('church')?.newValue}
          hasPendingChange={!!getPendingModification('church')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('church')?.id}
        />
        <Field 
          label="Sesiune foto-video" 
          value={project.session} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('session')?.newValue}
          hasPendingChange={!!getPendingModification('session')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('session')?.id}
        />
        <Field 
          label="Restaurant" 
          value={project.restaurant} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('restaurant')?.newValue}
          hasPendingChange={!!getPendingModification('restaurant')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('restaurant')?.id}
        />
        <Field 
          label="Alte detalii" 
          value={project.detailsExtra} 
          editable 
          projectId={project.id}
          pendingValue={getPendingModification('detailsExtra')?.newValue}
          hasPendingChange={!!getPendingModification('detailsExtra')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('detailsExtra')?.id}
        />
      </div>
      <p className="text-xs text-gray-500 mt-3">
        Modificările propuse de client apar după aprobare.
      </p>
    </div>
  );
}

function EditareTab({ project }: { project: Project }) {
  const [editingPreferences, setEditingPreferences] = useState(false);
  const [preferences, setPreferences] = useState(project.editingPreferences || '');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setPreferences(project.editingPreferences || '');
  }, [project.editingPreferences]);

  const handleSavePreferences = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/projects/${project.id}/update`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field: 'editingPreferences',
          value: preferences,
        }),
      });

      if (response.ok) {
        setEditingPreferences(false);
        window.location.reload();
      } else {
        console.error('Failed to save preferences');
        alert('Eroare la salvare. Încercați din nou.');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      alert('Eroare la salvare. Încercați din nou.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelPreferences = () => {
    setPreferences(project.editingPreferences || '');
    setEditingPreferences(false);
  };

  return (
    <div className="space-y-3">
      <div className="bg-gray-800 p-4 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">Status editare</div>
          <StatusBadge status={project.editStatus as "IN_PROGRES" | "IN_ASTEPTARE" | "PARTIAL" | "FINALIZATA"} />
        </div>
      </div>
      <div className="bg-gray-800 p-4 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm text-gray-400">Preferințe editare</div>
          {!editingPreferences && (
            <button 
              onClick={() => setEditingPreferences(true)}
              className="px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded text-xs font-medium"
            >
              editează
            </button>
          )}
        </div>
        {editingPreferences ? (
          <div>
            <textarea
              className="w-full bg-gray-900 border border-gray-700 rounded-md p-2 h-40 focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Scrieți aici toate detaliile pe care le considerați necesare pentru editare. Exemplu: ceremonia mai scurtă, melodii pentru fundal sau trailer etc"
              value={preferences}
              onChange={(e) => setPreferences(e.target.value)}
              disabled={isLoading}
            />
            <div className="mt-2 flex gap-2">
              <button 
                onClick={handleSavePreferences}
                disabled={isLoading}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-sm font-medium disabled:bg-gray-500"
              >
                {isLoading ? 'Se salvează...' : 'Salvează'}
              </button>
              <button 
                onClick={handleCancelPreferences}
                disabled={isLoading}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md text-sm font-medium"
              >
                Anulează
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-gray-900 border border-gray-700 rounded-md p-2 h-40 text-sm text-gray-300">
            {preferences || "Nu au fost specificate preferințe pentru editare."}
          </div>
        )}
      </div>
    </div>
  );
}

function FilmeTab({
  project,
  isAdmin,
}: {
  project: ProjectWithFiles;
  isAdmin: boolean;
}) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="p-2">Nume fișier</th>
            <th className="p-2">Mărime</th>
            <th className="p-2">Acțiuni</th>
          </tr>
        </thead>
        <tbody>
          {project.files.map((f) => (
            <tr key={f.id} className="border-b border-gray-700">
              <td className="p-2">{f.displayName}</td>
              <td className="p-2">
                {Math.round(Number(f.sizeBytes) / (1024 * 1024))} MB
              </td>
              <td className="p-2">
                <a
                  className="underline text-indigo-400 hover:text-indigo-300"
                  href={`/api/files/${f.id}/download`}
                >
                  Descarcă
                </a>
              </td>
            </tr>
          ))}
          {project.files.length === 0 && (
            <tr>
              <td colSpan={3} className="p-4 text-center text-gray-500">
                Nu există fișiere încă.
              </td>
            </tr>
          )}
        </tbody>
      </table>
      {isAdmin && (
        <div className="mt-3">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-sm font-medium">
            Încarcă fișier
          </button>
        </div>
        
      )}
    </div>
  );
}