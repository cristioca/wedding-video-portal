"use client";

import { useState } from "react";
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
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(value || "");

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
          alert(result.message || 'Modificarea a fost trimisă pentru aprobare de către Videograf.');
          window.location.reload();
        }
      } else {
        console.error('Failed to save field');
        alert('Eroare la salvare. Încercați din nou.');
      }
    } catch (error) {
      console.error('Error saving field:', error);
      alert('Eroare la salvare. Încercați din nou.');
    }
  };

  // Helper function to map Romanian labels to field names
  const getFieldName = (label: string): string => {
    const fieldMap: { [key: string]: string } = {
      'Data evenimentului': 'eventDate',
      'Titlu video': 'titleVideo',
      'Oraș': 'city',
      'Căsătorie civilă': 'civilDate',
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
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-md px-2 py-1 text-sm focus:ring-indigo-500 focus:border-indigo-500"
              autoFocus
            />
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
              <div className="font-medium">{value || "-"}</div>
            )}
          </div>
        )}
      </div>
      {editable && !isEditing && (
        <button 
          onClick={() => setIsEditing(true)}
          className="text-sm underline hover:text-indigo-400"
        >
          editează
        </button>
      )}
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

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
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
          value={
            project.civilSameDay
              ? "aceeași zi"
              : project.civilDate?.toISOString().slice(0, 10) || "-"
          }
          editable
          projectId={project.id}
          pendingValue={getPendingModification('civilDate')?.newValue}
          hasPendingChange={!!getPendingModification('civilDate')}
          isAdmin={isAdmin}
          modificationId={getPendingModification('civilDate')?.id}
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
  return (
    <div className="space-y-3">
      <div className="bg-gray-800 p-4 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">Status editare</div>
          <StatusBadge status={project.editStatus as "IN_PROGRES" | "IN_ASTEPTARE" | "PARTIAL" | "FINALIZATA"} />
        </div>
      </div>
      <div className="bg-gray-800 p-4 rounded-lg">
        <div className="text-sm text-gray-400 mb-2">Preferințe editare</div>
        <textarea
          className="w-full bg-gray-900 border border-gray-700 rounded-md p-2 h-40 focus:ring-indigo-500 focus:border-indigo-500"
          placeholder="Scrieți aici toate detaliile pe care le considerați necesare pentru editare. Exemplu: ceremonia mai scurtă, melodii pentru fundal sau trailer etc"
        ></textarea>
        <div className="mt-2 flex justify-end">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-sm font-medium">
            Salvează
          </button>
        </div>
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
    </div>)}