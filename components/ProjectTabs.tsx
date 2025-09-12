"use client";

import { useState } from "react";
import type { Project, File as FileModel } from "@prisma/client";
import StatusBadge from "./StatusBadge";

// The component expects a single project, not an array
type ProjectWithFiles = Project & { files: FileModel[] };

type Props = {
  project: ProjectWithFiles;
  userRole: "ADMIN" | "CLIENT";
};

export default function ProjectTabs({ project, userRole }: Props) {
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

      {tab === "detalii" && <DetaliiTab project={project} />}
      {tab === "editare" && <EditareTab project={project} />}
      {tab === "filme" && <FilmeTab project={project} isAdmin={isAdmin} />}
    </div>
  );
}

function Field({
  label,
  value,
  editable = false,
}: {
  label: string;
  value?: string | null;
  editable?: boolean;
}) {
  return (
    <div className="flex items-start justify-between gap-3 py-2 border-b border-[#252a35]">
      <div>
        <div className="text-sm text-gray-400">{label}</div>
        <div className="font-medium">{value || "-"}</div>
      </div>
      {editable && <button className="text-sm underline">editează</button>}
    </div>
  );
}

function DetaliiTab({ project }: { project: Project }) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2">
        <Field
          label="Data evenimentului"
          value={project.eventDate.toISOString().slice(0, 10)}
          editable
        />
        <Field
          label="Tip eveniment"
          value={project.type === "NUNTA" ? "nuntă" : "botez"}
        />
        <Field label="Titlu video" value={project.titleVideo} editable />
        <Field label="Oraș" value={project.city} editable />
        <Field
          label="Căsătorie civilă"
          value={
            project.civilSameDay
              ? "aceeași zi"
              : project.civilDate?.toISOString().slice(0, 10) || "-"
          }
          editable
        />
        <Field label="Pregătiri" value={project.prep} editable />
        <Field label="Biserica" value={project.church} editable />
        <Field label="Sesiune foto-video" value={project.session} editable />
        <Field label="Restaurant" value={project.restaurant} editable />
        <Field label="Alte detalii" value={project.detailsExtra} editable />
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