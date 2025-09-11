import { NextRequest } from "next/server";
import { prisma } from "@/lib/db";

export async function GET(req: NextRequest, { params }: { params: { id: string } }) {
  // TODO: validate session and stream file from storage
  const file = await prisma.file.findUnique({ where: { id: params.id } });
  if (!file) return new Response("Not Found", { status: 404 });
  await prisma.fileDownloadEvent.create({
    data: { fileId: file.id, projectId: file.projectId, success: false }
  });
  return new Response(null, { status: 204 });
}
