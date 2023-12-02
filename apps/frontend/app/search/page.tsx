import { searchParamSchema } from './schema';
import { LayoutTabs } from './LayoutTabs';
import uniqBy from 'lodash.uniqby';
import { Error } from './SearchError';
import { PlayerList } from '../../components/PlayerList';
import prisma from '../../utils/prisma';

export const metadata = {
  title: 'Search - Players',
  description: 'Search for players',
};

export default async function Index({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const { query } = searchParamSchema.parse(searchParams);

  if (query.length < 2) {
    return <Error message="Please enter at least 2 characters." />;
  }

  const matches = await prisma.$transaction([
    prisma.player.findMany({
      where: {
        name: {
          equals: query,
          mode: 'insensitive',
        },
      },
      select: {
        name: true,
        playTime: true,
        clanName: true,
      },
      orderBy: {
        name: 'asc',
      },
      take: 100,
    }),
    prisma.player.findMany({
      where: {
        OR: [
          {
            name: {
              startsWith: query,
              mode: 'insensitive',
            },
          },
          {
            name: {
              endsWith: query,
              mode: 'insensitive',
            },
          },
        ],
      },
      select: {
        name: true,
        playTime: true,
        clanName: true,
      },
      orderBy: {
        name: 'asc',
      },
      take: 100,
    }),
    prisma.player.findMany({
      where: {
        name: {
          contains: query,
          mode: 'insensitive',
        },
      },
      select: {
        name: true,
        playTime: true,
        clanName: true,
      },
      orderBy: {
        name: 'asc',
      },
      take: 100,
    }),
  ]);

  const players = uniqBy(matches.flat(), 'name').slice(0, 100);

  return (
    <LayoutTabs query={query} selectedTab="players">
      {({ playerCount }) => (
        <PlayerList
          playerCount={playerCount}
          rankMethod={null}
          players={players.map((player, index) => ({
            rank: index + 1,
            name: player.name,
            clan: player.clanName ?? undefined,
            rating: undefined,
            playTime: player.playTime,
          }))}
        />
      )}
    </LayoutTabs>
  );
}
