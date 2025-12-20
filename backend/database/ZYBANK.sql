
/*==============================================================*/
/* Table: ACCOUNT                                               */
/*==============================================================*/
create table ACCOUNT
(
   ACCOUNT_ID           varchar(10) not null  comment '',
   MORTAGE_ACC_ID       varchar(10)  comment '',
   USER_ID              varchar(10)  comment '',
   SAVING_ACC_ID        varchar(10)  comment '',
   ACCOUNT_TYPE         text  comment '',
   BALANCE              float  comment '',
   INTEREST_RATE        float  comment '',
   CREATED_AT           datetime  comment '',
   STATUS               text  comment '',
   ACCOUNT_NUMBER       text  comment '',
   primary key (ACCOUNT_ID)
);

/*==============================================================*/
/* Table: BILL                                                  */
/*==============================================================*/
create table BILL
(
   BILL_ID              varchar(10) not null  comment '',
   PROVIDER             varchar(100)  comment '',
   AMOUNT_DUE           datetime  comment '',
   STATUS               text  comment '',
   DUE_DATE             datetime  comment '',
   CREATED_AT           datetime  comment '',
   primary key (BILL_ID)
);

/*================== Table: EKYC ================================*/
CREATE TABLE EKYC (
    EKYC_ID varchar(10) NOT NULL,
    USER_ID varchar(10),
    IMG_FRONT_URL text,
    IMG_BACK_URL text,
    SELFIE_URL text,
    STATUS text,
    REVIEWED_AT varchar(30),
    REVIEWED_BY varchar(30),
    CREATED_AT datetime,
    PRIMARY KEY (EKYC_ID)
);

/*==============================================================*/
/* Table: EXTERNAL_ACCOUNT                                      */
/*==============================================================*/
create table EXTERNAL_ACCOUNT
(
   EX_ACC_ID            varchar(10) not null  comment '',
   BANK_CODE            text  comment '',
   ACCOUNT_NUMBER       text  comment '',
   ACCOUNT_NAME         text  comment '',
   primary key (EX_ACC_ID)
);

/*==============================================================*/
/* Table: LOCATION                                              */
/*==============================================================*/
create table LOCATION
(
   BRANCH_ID            varchar(10) not null  comment '',
   NAME                 text  comment '',
   ADDRESS              text  comment '',
   LAT                  float  comment '',
   LNG                  float  comment '',
   OPEN_HOURS           varchar(30)  comment '',
   CREATED_AT           datetime  comment '',
   primary key (BRANCH_ID)
);

/*================== Table: MORTAGE_DETAIL ======================*/
CREATE TABLE MORTAGE_DETAIL (
    MORTAGE_ACC_ID varchar(10) NOT NULL,
    ACCOUNT_ID varchar(10),
    TOTAL_LOAN_AMOUNT float,
    REMAINING_BALANCE float,
    PAYMEN_FREQUENCY varchar(20),
    PAYMENT_AMOUNT float,
    NEXT_PAYMENT_DATE datetime,
    LOAN_END_DATE datetime,
    PRIMARY KEY (MORTAGE_ACC_ID)
);

/*==============================================================*/
/* Table: TRANSACTIONS                                          */
/*==============================================================*/
create table TRANSACTIONS
(
   TRANSACTION_ID       varchar(10) not null  comment '',
   PAYMENT_ID           varchar(10)  comment '',
   ACCOUNT_ID           varchar(10)  comment '',
   AMOUNT               float  comment '',
   CURRENCY             varchar(100)  comment '',
   ACCOUNT_TYPE         text  comment '',
   STATUS               text  comment '',
   CREATED_AT           datetime  comment '',
   COMPLETE_AT          datetime  comment '',
   DEST_ACC_NUM         varchar(20)  comment '',
   DEST_ACC_NAME        text  comment '',
   DEST_BANK_CODE       varchar(20)  comment '',
   TYPE                 text  comment '',
   primary key (TRANSACTION_ID)
);

/*==============================================================*/
/* Table: USER                                                  */
/*==============================================================*/
create table USER
(
   USER_ID              varchar(10) not null  comment '',
   BIOMETRIC_ID         varchar(10)  comment '',
   EKYC_ID              varchar(10)  comment '',
   FULL_NAME            text  comment '',
   EMAIL                text  comment '',
   PHONE                text  comment '',
   ROLE                 text  comment '',
   CREATED_AT           datetime  comment '',
   PASSWORD             text  comment '',
   IS_ACTIVE            bool  comment '',
   primary key (USER_ID)
);

/*==============================================================*/
/* Table: USER_BIOMETRIC                                        */
/*==============================================================*/
create table USER_BIOMETRIC
(
   BIOMETRIC_ID         varchar(10) not null  comment '',
   USER_ID              varchar(10)  comment '',
   FACE_TEMPLATE_HASH   text  comment '',
   DEVICE_BIOMETRIC     bool  comment '',
   FACE_ENABLED         bool  comment '',
   CREATED_AT           datetime  comment '',
   primary key (BIOMETRIC_ID)
);

/*==============================================================*/
/* Table: UTILITY_PAYMENT                                       */
/*==============================================================*/
create table UTILITY_PAYMENT
(
   UTILITY_PAYMENT_ID   varchar(10) not null  comment '',
   TRANSACTION_ID       varchar(10)  comment '',
   PROVIDER_CODE        varchar(50)  comment '',
   REFERENCE_CODE_1     varchar(100)  comment '',
   REFERENCE_CODE_2     varchar(100)  comment '',
   CREATED_AT           datetime  comment '',
   primary key (UTILITY_PAYMENT_ID)
);

/*================== Table: REFRESH_TOKEN ======================*/ 
CREATE TABLE REFRESH_TOKEN 
( 
ID INT AUTO_INCREMENT PRIMARY KEY,
 USER_ID varchar(10) NOT NULL,
 TOKEN text NOT NULL,
 CREATED_AT datetime NOT NULL,
 EXPIRES_AT datetime NOT NULL,
 REVOKED bool DEFAULT 0 
);

/*================== Table: TOKEN_BLACKLIST ====================*/
CREATE TABLE TOKEN_BLACKLIST (
  TOKEN varchar(255) NOT NULL,
  BLACKLISTED_AT datetime NOT NULL,
  PRIMARY KEY (TOKEN)
);

CREATE TABLE SAVING_DETAIL
(
   SAVING_ACC_ID      varchar(10) NOT NULL,
   ACCOUNT_ID         varchar(10),
   PRINCIPAL_AMOUNT   float,
   INTEREST_RATE      float,
   TERM_MONTHS        int,
   START_DATE         datetime,
   MATURITY_DATE      datetime,
   PRIMARY KEY (SAVING_ACC_ID)
);
