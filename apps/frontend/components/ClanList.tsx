import { List, ListCell } from '@teerank/frontend/components/List';
import { formatInteger, formatPlayTime } from '@teerank/frontend/utils/format';

export function ClanList({
  clans,
}: {
  clans: {
    rank: number;
    name: string;
    playerCount: number;
    playTime: number;
  }[];
}) {
  const columns = [
    {
      title: '',
      expand: false,
    },
    {
      title: 'Name',
      expand: true,
    },
    {
      title: 'Players',
      expand: true,
    },
    {
      title: 'Play Time',
      expand: false,
    },
  ];

  return (
    <List columns={columns}>
      {clans.map((clan) => (
        <>
          <ListCell alignRight label={formatInteger(clan.rank)} />
          <ListCell
            label={clan.name}
            href={{
              pathname: `/clan/${encodeURIComponent(clan.name)}`,
            }}
          />
          <ListCell alignRight label={formatInteger(clan.playerCount)} />
          <ListCell alignRight label={formatPlayTime(clan.playTime)} />
        </>
      ))}
    </List>
  );
}