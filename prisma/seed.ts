import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  console.log('Start seeding...');

  // --- Clean up previous data to avoid duplicates ---
  // Deleting projects first because they depend on users
  await prisma.project.deleteMany();
  // Deleting non-admin users
  await prisma.user.deleteMany({
    where: {
      email: {
        not: 'admin@admin.com',
      },
    },
  });
  console.log('Cleaned up old projects and client users.');

  // --- Create Admin User ---
  const adminEmail = 'admin@admin.com';
  const adminHashedPassword = await bcrypt.hash('password123', 10);
  const adminUser = await prisma.user.upsert({
    where: { email: adminEmail },
    update: { password: adminHashedPassword }, // Ensure password is correct
    create: {
      email: adminEmail,
      password: adminHashedPassword,
      name: 'Admin User',
    },
  });
  console.log(`Upserted admin user: ${adminUser.email}`);

  // --- Create Client User ---
  const clientEmail = 'client@client.com';
  const clientHashedPassword = await bcrypt.hash('password123', 10);
  const clientUser = await prisma.user.create({
    data: {
      email: clientEmail,
      password: clientHashedPassword,
      name: 'Client User',
    },
  });
  console.log(`Created client user: ${clientUser.email}`);

  // --- Create Projects ---
  await prisma.project.create({
    data: {
      name: 'Nunta Popescu',
      status: 'Editing',
      dueDate: new Date('2025-10-20'),
      eventDate: new Date('2025-09-15'),
      type: 'NUNTA',
      titleVideo: 'Andrei & Maria Popescu',
      city: 'Bucuresti',
      editStatus: 'IN_PROGRES',
      user: {
        connect: { id: adminUser.id }, // Connect to admin user
      },
    },
  });
  console.log('Created project for admin user.');

  await prisma.project.create({
    data: {
      name: 'Botez Ionescu',
      status: 'Planning',
      dueDate: new Date('2025-11-30'),
      eventDate: new Date('2025-11-05'),
      type: 'BOTEZ',
      titleVideo: 'Micul Matei Ionescu',
      city: 'Cluj-Napoca',
      editStatus: 'IN_ASTEPTARE',
      user: {
        connect: { id: clientUser.id }, // Connect to client user
      },
    },
  });
  console.log('Created project for client user.');

  console.log('Seeding finished.');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });