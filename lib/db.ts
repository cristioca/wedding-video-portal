import { PrismaClient } from '@prisma/client';

// Declare a global variable to hold the Prisma client instance.
// This is done to prevent creating new connections on every hot reload in development.
declare global {
  // eslint-disable-next-line no-var
  var prisma: PrismaClient | undefined;
}

// Check if we are in production or development.
// If a prisma instance already exists on the global object, use it.
// Otherwise, create a new PrismaClient.
export const db = globalThis.prisma || new PrismaClient();

// In development, assign the new client to the global object.
if (process.env.NODE_ENV !== 'production') {
  globalThis.prisma = db;
}