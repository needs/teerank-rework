import { Tab, Tabs } from '@teerank/frontend/components/Tabs';
import prisma from '@teerank/frontend/utils/prisma';
import React from 'react';

export async function LayoutTabs({
  children,
  query,
  selectedTab,
}: {
  children: (counts: { playerCount: number, clanCount: number, gameServerCount: number }) => React.ReactNode;
  query: string;
  selectedTab: 'players' | 'clans' | 'servers';
}) {
  const [playerCount, clanCount, gameServerCount] = await prisma.$transaction([
    prisma.player.count({
      where: {
        name: {
          contains: query,
        },
      },
    }),
    prisma.clan.count({
      where: {
        name: {
          contains: query,
        },
      },
    }),
    prisma.gameServer.count({
      where: {
        lastSnapshot: {
          name: {
            contains: query,
          },
        },
      },
    }),
  ]);

  return (
    <div className="flex flex-col gap-4 py-8">
      <Tabs>
        <Tab
          label="Players"
          count={playerCount}
          isActive={selectedTab === 'players'}
          href={{
            pathname: '/search',
            query: { query },
          }}
        />
        <Tab
          label="Clans"
          count={clanCount}
          isActive={selectedTab === 'clans'}
          href={{ pathname: '/search/clans', query: { query } }}
        />
        <Tab
          label="Servers"
          count={gameServerCount}
          isActive={selectedTab === 'servers'}
          href={{ pathname: '/search/servers', query: { query } }}
        />
      </Tabs>
      {children({ playerCount, clanCount, gameServerCount })}
    </div>
  );
}