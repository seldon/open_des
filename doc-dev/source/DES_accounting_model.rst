Overview
========

The DES accounting model adopted by OpenDES is a concrete implementation of the generic accounting model at the hearth of the django-simple-accounting_ app.

In fact, django-simple-accounting_ was designed and developed with a DES-like scenario in mind: i.e., multiple economic actors and complex money flows amongst them.

Economic subjects
================

In a DES, there are three primary kinds of economic actors (o, as we like to say, **economic subjects**): People_, GASs_ and Suppliers_.  

Each economic subject can exchange money, goods and services with other economic subjects within the same (or another) DES;  money flows between economic subjects are called **transactions**. 

In order to record and manage transactions, we need the concept of **account**.  An account is just a way to group and label transactions between economic subjects: a transaction can be described as a money flow from a source account to one or more target accounts, potentially passing through intermediate accounts.  Each account belongs to one (and only one) economic subject, the account's owner; accounts belonging to a given subject are organized in tree-like structure (**account hierarchy**) and together made what we call the subject's **accounting system**.

Accounts  can be of one of two very different types:
* **stock-like** accounts represent amounts of money owned by the subject. By convention, if these amounts are positive they are called *assets* (e.g. cash in wallet), while if negative they are called **liabilities** (e.g. a debt);
* **flux-like** accounts are similar to counters recording money flows *between* different accounting systems

Generally, a transaction involves at least 2 accounts; more complex transaction can involve up to ``3n + 1`` accounts, where ``n`` is the number of splits constituting the transaction itself.

Every robust accounting solution should implement what is know as **double-entry** accounting: in a nutshell, double-entry accounting - in its simplest form --  requires that every transaction generates two accounting records: one for both the source and target accounts.  This way, integrity of accounting records is automatically enforced (i.e. no money amount can disappear or be created from the vacuum).  In more general setups - as the DES one - transactions may involve more than 2 accounts, so more than two accounting records may be created for the transaction (one for each of the involved accounts). Such accounting records are called **ledger entries**, since they can be thought of as entries in a ledger associated to the given account.


Account hierarchies
===================

People
------

GASs
---

Suppliers
---------

Common transactions
===================

Person <--> GAS
---------------

GAS <--> GAS
---------------

GAS <--> Supplier
---------------


.. _django-simple-accounting: https://github.com/seldon/django-simple-accounting
