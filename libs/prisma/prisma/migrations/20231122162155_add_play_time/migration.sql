-- AlterTable
ALTER TABLE `PlayerInfo` ADD COLUMN `playTime` INTEGER NOT NULL DEFAULT 0,
    MODIFY `rating` DOUBLE NULL;