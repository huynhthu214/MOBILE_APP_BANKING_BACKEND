/*==============================================================*/
/* DBMS name:      MySQL 5.0                                    */
/* Created on:     05/12/2025 9:15:38 PM                        */
/*==============================================================*/


alter table ACCOUNT 
   drop foreign key FK_ACCOUNT_USER_ACCO_USER;

alter table BILL 
   drop foreign key FK_BILL_BILL_BILL_BILL_PAY;

alter table BILL_PAYMENT 
   drop foreign key FK_BILL_PAY_BILL_BILL_BILL;

alter table BILL_PAYMENT 
   drop foreign key FK_BILL_PAY_TRANSAC_P_TRANSACT;

alter table EKYC 
   drop foreign key FK_EKYC_USER_EKYC_USER;

alter table MORTAGE_DETAIL 
   drop foreign key FK_MORTAGE__ACCOUNT_M_ACCOUNT;

alter table OTP 
   drop foreign key FK_OTP_USER_OTP_USER;

alter table SAVING_DETAIL 
   drop foreign key FK_SAVING_D_ACCOUNT_S_ACCOUNT;

alter table TRANSACTION 
   drop foreign key FK_TRANSACT_ACCOUNT_T_ACCOUNT;

alter table TRANSACTION 
   drop foreign key FK_TRANSACT_TRANSAC_P_BILL_PAY;

alter table USER 
   drop foreign key FK_USER_USER_EKYC_EKYC;

alter table UTILITY_PAYMENT 
   drop foreign key FK_UTILITY__TRANSAC_U_TRANSACT;


alter table ACCOUNT 
   drop foreign key FK_ACCOUNT_USER_ACCO_USER;

drop table if exists ACCOUNT;


alter table BILL 
   drop foreign key FK_BILL_BILL_BILL_BILL_PAY;

drop table if exists BILL;


alter table BILL_PAYMENT 
   drop foreign key FK_BILL_PAY_BILL_BILL_BILL;

alter table BILL_PAYMENT 
   drop foreign key FK_BILL_PAY_TRANSAC_P_TRANSACT;

drop table if exists BILL_PAYMENT;


alter table EKYC 
   drop foreign key FK_EKYC_USER_EKYC_USER;

drop table if exists EKYC;

drop table if exists LOCATION;


alter table MORTAGE_DETAIL 
   drop foreign key FK_MORTAGE__ACCOUNT_M_ACCOUNT;

drop table if exists MORTAGE_DETAIL;


alter table OTP 
   drop foreign key FK_OTP_USER_OTP_USER;

drop table if exists OTP;


alter table SAVING_DETAIL 
   drop foreign key FK_SAVING_D_ACCOUNT_S_ACCOUNT;

drop table if exists SAVING_DETAIL;


alter table TRANSACTION 
   drop foreign key FK_TRANSACT_ACCOUNT_T_ACCOUNT;

alter table TRANSACTION 
   drop foreign key FK_TRANSACT_TRANSAC_P_BILL_PAY;

drop table if exists TRANSACTION;


alter table USER 
   drop foreign key FK_USER_USER_EKYC_EKYC;

drop table if exists USER;


alter table UTILITY_PAYMENT 
   drop foreign key FK_UTILITY__TRANSAC_U_TRANSACT;

drop table if exists UTILITY_PAYMENT;

/*==============================================================*/
/* Table: ACCOUNT                                               */
/*==============================================================*/
create table ACCOUNT
(
   ACCOUNT_ID           varchar(10) not null  comment '',
   USER_ID              varchar(10)  comment '',
   ACCOUNT_TYPE         text  comment '',
   BALANCE              float  comment '',
   INTEREST_RATE        float  comment '',
   CREATED_AT           datetime  comment '',
   STATUS               text  comment '',
   ACCOUNT_NUMBER       char(10)  comment '',
   primary key (ACCOUNT_ID)
);

/*==============================================================*/
/* Table: BILL                                                  */
/*==============================================================*/
create table BILL
(
   BILL_ID              varchar(10) not null  comment '',
   PAYMENT_ID           varchar(10)  comment '',
   PROVIDER             varchar(100)  comment '',
   AMOUNT_DUE           datetime  comment '',
   STATUS               text  comment '',
   DUE_DATE             datetime  comment '',
   CREATED_AT           datetime  comment '',
   primary key (BILL_ID)
);

/*==============================================================*/
/* Table: BILL_PAYMENT                                          */
/*==============================================================*/
create table BILL_PAYMENT
(
   PAYMENT_ID           varchar(10) not null  comment '',
   TRANSACTION_ID       varchar(10)  comment '',
   BILL_ID              varchar(10)  comment '',
   PAID_AT              datetime  comment '',
   primary key (PAYMENT_ID)
);

/*==============================================================*/
/* Table: EKYC                                                  */
/*==============================================================*/
create table EKYC
(
   EKYC_ID              varchar(10) not null  comment '',
   USER_ID              varchar(10)  comment '',
   IMG_FRONT_URL        text  comment '',
   IMG_BACK_URL         text  comment '',
   SELFIE_URL           text  comment '',
   STATUS               text  comment '',
   REVIEWED_AT          varchar(30)  comment '',
   REVIEWED_BY          varchar(30)  comment '',
   CREATED_AT           datetime  comment '',
   primary key (EKYC_ID)
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

/*==============================================================*/
/* Table: MORTAGE_DETAIL                                        */
/*==============================================================*/
create table MORTAGE_DETAIL
(
   MORTAGE_ACC_ID       varchar(10) not null  comment '',
   ACCOUNT_ID           varchar(10)  comment '',
   TOTAL_LOAN_AMOUNT    float  comment '',
   REMAINING_BALANCE    float  comment '',
   PAYMEN_FREQUENCY     varchar(20)  comment '',
   PAYMENT_AMOUNT       float  comment '',
   NEXT_PAYMENT_DATE    datetime  comment '',
   LOAN_END_DATE        datetime  comment '',
   primary key (MORTAGE_ACC_ID)
);

/*==============================================================*/
/* Table: OTP                                                   */
/*==============================================================*/
create table OTP
(
   OTP_ID               varchar(10) not null  comment '',
   USER_ID              varchar(10)  comment '',
   CODE                 varchar(10)  comment '',
   PURPOSE              text  comment '',
   CREATED_AT           datetime  comment '',
   EXPIRES_AT           datetime  comment '',
   IS_USED              bool  comment '',
   primary key (OTP_ID)
);

/*==============================================================*/
/* Table: SAVING_DETAIL                                         */
/*==============================================================*/
create table SAVING_DETAIL
(
   SAVING_ACC_ID        varchar(10) not null  comment '',
   ACCOUNT_ID           varchar(10)  comment '',
   PRINCIPAL_AMOUNT     float  comment '',
   INTEREST_RATE        float  comment '',
   TERM_MONTHS          int  comment '',
   START_DATE           datetime  comment '',
   MATURITY_DATE        datetime  comment '',
   primary key (SAVING_ACC_ID)
);

/*==============================================================*/
/* Table: TRANSACTION                                           */
/*==============================================================*/
create table TRANSACTION
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
   EKYC_ID              varchar(10)  comment '',
   FULL_NAME            text  comment '',
   EMAIL                text  comment '',
   PHONE                text  comment '',
   ROLE                 text  comment '',
   CREATED_AT           datetime  comment '',
   IS_ACTIVE            bool  comment '',
   PASSWORD             text  comment '',
   primary key (USER_ID)
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

alter table ACCOUNT add constraint FK_ACCOUNT_USER_ACCO_USER foreign key (USER_ID)
      references USER (USER_ID) on delete restrict on update restrict;

alter table BILL add constraint FK_BILL_BILL_BILL_BILL_PAY foreign key (PAYMENT_ID)
      references BILL_PAYMENT (PAYMENT_ID) on delete restrict on update restrict;

alter table BILL_PAYMENT add constraint FK_BILL_PAY_BILL_BILL_BILL foreign key (BILL_ID)
      references BILL (BILL_ID) on delete restrict on update restrict;

alter table BILL_PAYMENT add constraint FK_BILL_PAY_TRANSAC_P_TRANSACT foreign key (TRANSACTION_ID)
      references TRANSACTION (TRANSACTION_ID) on delete restrict on update restrict;

alter table EKYC add constraint FK_EKYC_USER_EKYC_USER foreign key (USER_ID)
      references USER (USER_ID) on delete restrict on update restrict;

alter table MORTAGE_DETAIL add constraint FK_MORTAGE__ACCOUNT_M_ACCOUNT foreign key (ACCOUNT_ID)
      references ACCOUNT (ACCOUNT_ID) on delete restrict on update restrict;

alter table OTP add constraint FK_OTP_USER_OTP_USER foreign key (USER_ID)
      references USER (USER_ID) on delete restrict on update restrict;

alter table SAVING_DETAIL add constraint FK_SAVING_D_ACCOUNT_S_ACCOUNT foreign key (ACCOUNT_ID)
      references ACCOUNT (ACCOUNT_ID) on delete restrict on update restrict;

alter table TRANSACTION add constraint FK_TRANSACT_ACCOUNT_T_ACCOUNT foreign key (ACCOUNT_ID)
      references ACCOUNT (ACCOUNT_ID) on delete restrict on update restrict;

alter table TRANSACTION add constraint FK_TRANSACT_TRANSAC_P_BILL_PAY foreign key (PAYMENT_ID)
      references BILL_PAYMENT (PAYMENT_ID) on delete restrict on update restrict;

alter table USER add constraint FK_USER_USER_EKYC_EKYC foreign key (EKYC_ID)
      references EKYC (EKYC_ID) on delete restrict on update restrict;

alter table UTILITY_PAYMENT add constraint FK_UTILITY__TRANSAC_U_TRANSACT foreign key (TRANSACTION_ID)
      references TRANSACTION (TRANSACTION_ID) on delete restrict on update restrict;

