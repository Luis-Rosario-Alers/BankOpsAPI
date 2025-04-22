-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


-- -----------------------------------------------------
-- Schema bankops_banking
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `bankops_banking` ;
USE `bankops_banking` ;

-- -----------------------------------------------------
-- Table `bankops_banking`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bankops_banking`.`user` (
  `user_id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `email` VARCHAR(100) NULL DEFAULT NULL,
  `password_hash` BLOB NOT NULL,
  `password_salt` BLOB NULL DEFAULT NULL,
  `roles` ENUM('CUSTOMER', 'ADMIN') NOT NULL DEFAULT 'CUSTOMER',
  `last_login` DATETIME NULL DEFAULT NULL,
  `is_active` TINYINT(4) NOT NULL DEFAULT 0,
  `failed_login_attempts` INT(11) NULL DEFAULT NULL,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  `last_password_change` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `user_id_UNIQUE` (`user_id` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 3;


-- -----------------------------------------------------
-- Table `bankops_banking`.`account`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bankops_banking`.`account` (
  `account_number` INT(11) NOT NULL AUTO_INCREMENT,
  `account_name` VARCHAR(50) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `account_holder` VARCHAR(45) NOT NULL,
  `account_type` ENUM('CHECKING', 'SAVINGS', 'CERTIFICATE OF DEPOSIT') NULL DEFAULT NULL,
  `creation_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  `balance` DECIMAL(13,2) NULL DEFAULT NULL,
  `interest_rate` DECIMAL(6,3) NULL DEFAULT NULL,
  `pin_salt` BLOB NOT NULL,
  `pin_hash` BLOB NOT NULL,
  `is_locked` TINYINT(4) NULL DEFAULT NULL,
  `latest_balance_change` DECIMAL(13,2) NOT NULL,
  `last_transaction_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  PRIMARY KEY (`account_number`, `user_id`, `account_holder`),
  UNIQUE INDEX `account_number_UNIQUE` (`account_number` ASC) VISIBLE,
  INDEX `user_id_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `bankops_banking`.`user` (`user_id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3;


-- -----------------------------------------------------
-- Table `bankops_banking`.`jwt_token`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bankops_banking`.`jwt_token` (
  `id` VARCHAR(36) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `is_blacklisted` TINYINT(4) NOT NULL,
  `created_at` DATETIME NOT NULL,
  `expires_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `user_id_idx` (`user_id` ASC) VISIBLE,
  CONSTRAINT `user_id`
    FOREIGN KEY (`user_id`)
    REFERENCES `bankops_banking`.`user` (`user_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bankops_banking`.`transaction`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bankops_banking`.`transaction` (
  `transaction_id` INT(11) NOT NULL AUTO_INCREMENT,
  `timestamp` DATETIME NOT NULL,
  `account_from` INT(11) NOT NULL,
  `account_to` INT(11) NOT NULL,
  `transaction_type` VARCHAR(20) NOT NULL,
  `amount` DECIMAL(13,2) NOT NULL,
  `balance_after` DECIMAL(13,2) NOT NULL,
  `description` VARCHAR(100) NULL DEFAULT NULL,
  `status` ENUM('PENDING', 'COMPLETED', 'FAILED', 'REVERSED') NULL DEFAULT 'PENDING',
  `reference_code` VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`transaction_id`),
  INDEX `idx_account_from` (`account_from` ASC) VISIBLE,
  INDEX `idx_account_to` (`account_to` ASC) VISIBLE,
  INDEX `idx_timestamp` (`timestamp` ASC) VISIBLE,
  CONSTRAINT `account_from`
    FOREIGN KEY (`account_from`)
    REFERENCES `bankops_banking`.`account` (`account_number`),
  CONSTRAINT `account_to`
    FOREIGN KEY (`account_to`)
    REFERENCES `bankops_banking`.`account` (`account_number`))
ENGINE = InnoDB
AUTO_INCREMENT = 3;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
