import { JobType } from "@prisma/client";
import { prisma } from "../prisma";
import { MAXIMUM_JOB_PER_SCHEDULE, scheduleJobBatches } from "../schedule";
import { compact} from 'lodash';

const BATCH_SIZE = 100;

export async function schedulePlayerRanking() {
  const offsets = Array.from({ length: MAXIMUM_JOB_PER_SCHEDULE }, (_, index) => index * BATCH_SIZE);

  const mostRecentUnrankedSnapshots = await prisma.$transaction(offsets.map(offset => prisma.gameServerSnapshot.findFirst({
    select: {
      id: true
    },
    where: {
      rankedAt: null,
    },
    orderBy: {
      createdAt: 'desc',
    },
    skip: offset,
  })));

  const batches = compact(mostRecentUnrankedSnapshots.map(snapshot => snapshot?.id));

  await scheduleJobBatches(JobType.RANK_PLAYERS, BATCH_SIZE, batches);
}
