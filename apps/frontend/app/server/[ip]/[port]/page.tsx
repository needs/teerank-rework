import { List, ListCell } from '@teerank/frontend/components/List';
import prisma from '@teerank/frontend/utils/prisma';
import { paramsSchema } from './schema';
import { z } from 'zod';
import { notFound } from 'next/navigation';
import { isIP, isIPv6 } from 'net';
import Link from 'next/link';

export const metadata = {
  title: 'Server',
  description: 'A Teeworlds server',
};

function ipAndPort(ip: string, port: number) {
  switch (isIP(ip)) {
    case 6:
      return `[${ip}]:${port}`;
    default:
      return `${ip}:${port}`;
  }
}

export default async function Index({
  params,
}: {
  params: z.infer<typeof paramsSchema>;
}) {
  const parsedParams = paramsSchema.parse(params);

  const gameServer = await prisma.gameServer.findUnique({
    where: {
      ip_port: {
        ip: parsedParams.ip,
        port: parsedParams.port,
      },
    },
    include: {
      lastSnapshot: {
        include: {
          clients: {
            orderBy: {
              score: 'desc',
            },
          },
          map: true,
        },
      },
    },
  });

  if (gameServer === null || gameServer.lastSnapshot === null) {
    return notFound();
  }

  return (
    <main className="flex flex-col gap-8 py-12">
      <header className="flex flex-row px-20 gap-8">
        <section className="flex flex-col gap-2 grow">
          <h1 className="text-2xl font-bold">{gameServer.lastSnapshot.name}</h1>
          <div className="flex flex-row divide-x">
            <span className="pr-4">
              <Link
                className="hover:underline"
                href={{
                  pathname: `/gametype/${encodeURIComponent(
                    gameServer.lastSnapshot.map.gameTypeName
                  )}`,
                }}
              >
                {gameServer.lastSnapshot.map.gameTypeName}
              </Link>
            </span>
            <span className="px-4">
              <Link
                className="hover:underline"
                href={{
                  pathname: `/gametype/${encodeURIComponent(
                    gameServer.lastSnapshot.map.gameTypeName
                  )}/map/${gameServer.lastSnapshot.map.name}`,
                }}
              >
                {gameServer.lastSnapshot.map.name}
              </Link>
            </span>
            <span className="px-4">{`${gameServer.lastSnapshot.numClients} / ${gameServer.lastSnapshot.maxClients} clients`}</span>
            <span className="px-4">{`${gameServer.lastSnapshot.numPlayers} players`}</span>
          </div>
        </section>
        <section className="flex flex-col divide-y border rounded-md overflow-hidde self-start">
          <h2 className="py-1.5 px-4 bg-gradient-to-b from-[#ffffff] to-[#eaeaea] text-center">
            Server address
          </h2>
          <span className="py-1.5 px-4 text-sm">
            {ipAndPort(gameServer.ip, gameServer.port)}
          </span>
        </section>
      </header>

      <List
        columns={[
          {
            title: '',
            expand: false,
          },
          {
            title: 'Name',
            expand: true,
          },
          {
            title: 'Clan',
            expand: true,
          },
          {
            title: 'Score',
            expand: false,
          },
        ]}
      >
        {gameServer.lastSnapshot.clients.map((client, index) => (
          <>
            <ListCell alignRight label={`${index + 1}`} />
            <ListCell
              label={client.playerName}
              href={{
                pathname: `/player/${encodeURIComponent(client.playerName)}`,
              }}
            />
            <ListCell label={client.clan} />
            <ListCell alignRight label={client.score.toString()} />
          </>
        ))}
      </List>
    </main>
  );
}