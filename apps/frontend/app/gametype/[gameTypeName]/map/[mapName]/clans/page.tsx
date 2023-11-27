import prisma from '@teerank/frontend/utils/prisma';
import { paramsSchema, searchParamsSchema } from '../schema';
import { notFound } from 'next/navigation';
import { ClanList } from '@teerank/frontend/components/ClanList';

export const metadata = {
  title: 'Clans',
  description: 'List of ranked clans',
};

export default async function Index({
  params,
  searchParams,
}: {
  params: { [key: string]: string };
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  const { page } = searchParamsSchema.parse(searchParams);
  const { gameTypeName, mapName } = paramsSchema.parse(params);

  const map = await prisma.map.findUnique({
    select: {
      _count: {
        select: {
          clanInfos: true,
        }
      },
      clanInfos: {
        select: {
          clan: {
            select: {
              _count: {
                select: {
                  players: true,
                },
              },
            },
          },
          clanName: true,
          playTime: true,
        },
        orderBy: [
          {
            playTime: 'desc',
          },
          {
            clan: {
              players: {
                _count: 'desc',
              },
            },
          },
        ],
        take: 100,
        skip: (page - 1) * 100,
      },
    },
    where: {
      name_gameTypeName: {
        name: mapName,
        gameTypeName: gameTypeName,
      },
    },
  });

  if (map === null) {
    return notFound();
  }

  return (
    <ClanList
      clanCount={map._count.clanInfos}
      clans={map.clanInfos.map((clanInfo, index) => ({
        rank: (page - 1) * 100 + index + 1,
        name: clanInfo.clanName,
        playerCount: clanInfo.clan._count.players,
        playTime: clanInfo.playTime,
      }))}
    />
  );
}
