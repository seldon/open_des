Overview
========

The DES accounting model adopted by OpenDES is a concrete implementation of the generic accounting model at the hearth of the django-simple-accounting_ app.

In fact, django-simple-accounting_ was designed and developed with a DES-like scenario in mind: i.e., multiple economic actors and complex money flows amongst them.

Economic subjects
=================

In a DES, there are three primary kinds of economic actors (o, as we like to say, **economic subjects**): People, GASs and Suppliers.  

Each economic subject can exchange money, goods and services with other economic subjects within the same (or another) DES;  money flows between economic subjects are called **transactions**. 

In order to record and manage transactions, we need the concept of **account**.  An account is just a way to group and label transactions between economic subjects: a transaction can be described as a money flow from a source account to one or more target accounts, potentially passing through intermediate accounts.  Each account belongs to one (and only one) economic subject, the account's owner; accounts belonging to a given subject are organized in tree-like structure (**account hierarchy**) and together made what we call the subject's **accounting system**.

Accounts  can be of one of two very different types:
* **stock-like** accounts represent amounts of money owned by the subject. By convention, if these amounts are positive they are called *assets* (e.g. cash in wallet), while if negative they are called **liabilities** (e.g. a debt);
* **flux-like** accounts are similar to counters recording money flows *between* different accounting systems

Generally, a transaction involves at least 2 accounts; more complex transaction can involve up to ``3n + 1`` accounts, where ``n`` is the number of splits constituting the transaction itself.

Every robust accounting solution should implement what is know as **double-entry** accounting: in a nutshell, double-entry accounting - in its simplest form --  requires that every transaction generates two accounting records: one for both the source and target accounts.  This way, integrity of accounting records is automatically enforced (i.e. no money amount can disappear or be created from the vacuum).  In more general setups - as the DES one - transactions may involve more than 2 accounts, so more than two accounting records may be created for the transaction (one for each of the involved accounts). Such accounting records are called **ledger entries**, since they can be thought of as entries in a ledger associated to the given account.


Account hierarchies
===================

Generalities
------------

As we said, every economic subject in a DES (people, GASs, suppliers) operates its own accounting system, made up of a hierarchy of accounts meant to record and organize transactions involving the subject itself.  Some general facts about account hierarchies (a.k.a. **account trees**):
- every account tree is rooted at a special account called `ROOT`;
- an account belonging in a given account tree can be referenced by a string (**account path**) describing the path to follow in the tree in order to reach the given account, starting from the root account; 
- account paths are constructed by joining account names with a delimiter, that we refer as the *account path separator*; hereafter, we assume that account names are separated by the `/` characters, but it can be easily configured [1]_;
- by convention, the root account of a tree has an empty path (i.e. `/`);
- each account (barring the root one) has one of four basic account types: **asset**, **liability**, **income**, **expense**, depending on its meaning within the accounting system it belongs to.  Remember that assets and liabilities are stock-like accounts (i.e., they represent amounts of money), while incomes and expenses are flux-like accounts (they act as counters for money flows between accounting systems);
- due to their own nature, stock-like accounts can contain only other stock-like accounts; the same is true for flux-like ones;
- an account is said to be a **placeholder account** if it can't (directly) contain transactions (strictly speaking, ledger entries), but it's only used as a way to group other accounts.

DES-specific account hierarchies
--------------------------------

Below, for every type of economic subject in a DES, we describe the corresponding hierarchy of accounts composing its accounting system. For the sake of clarity, we provide both a visual representation and some descriptive notes.

*Meaning of abbreviations*:
* A:= Asset
* L:= Liability
* I:= Income
* E:= Expense
* P:= Placeholder

People
------
From an accounting point of view, a person-like subject can be abstracted as:
* an asset-type account (*wallet*), (virtually) containing money the person is willing to inject in the DES's financial circuit (e.g. by making purchases as a GAS member)
* an expense-type hierarchy of accounts used to record money amounts flowing out his/her accounting system; in practice, payments (s)he makes to one of the GASs (s)he is member of (recall that a person can be member of multiple GASs); in turn, payments made to a GAS could represent:
 - recharges to the member own (virtual) pre-payed account in the GAS
 - payment of GAS's annual membership fees (if any)

::

      . ROOT (/)
      |----------- wallet [A]
      |
      +----------- expenses [P,E]+
				 |
      			         +--- gas [P, E] +
				      	      	 |
      				     	       	 +--- <UID gas #1>  [P, E]+
						 | 			  |
						 |  			  +--- recharges [E]
						 | ..			  |	 
						 | 			  +--- fees [E]
						 | 
						 | 
      		      				 +--- <UID gas #n>  [P, E]
						 			  |
						  			  +--- recharges [E]
						 			  |	 
						 			  +--- fees [E]
						 


GASs
----
A GAS's account hierarchy reflects the role played by the GAS itself in a DES: that of being an interface between people (purchasers) and suppliers (providers of goods and services). As every interface, a GAS is a "double-sided" entity: one side is person-facing, the other is supplier-facing.

The person-facing interface is based on the concept of *GAS membership*: a person can be member of more than one GAS, and this membership defines the details of the person <-> GAS relation.  From an accounting point of view, this relation is managed via three accounts:
- `/members/<member UID>` is a stock-like account representing the credit a person (as a GAS member) has against the GAS (s)he belongs to; this account may be thought as a pre-payed card from which the GAS draws when it need to pay suppliers (or other expenses related to GAS management)  
- `/incomes/recharges` is used to record recharges made by GAS members to their own "virtual pre-payed cards"
- `/incomes/fees` is used to record payment of annual membership fees by the GAS members (if required by the GAS)

The supplier-facing interface is made of two accounts:
- `/cash` is a stock-like account representing the actual money amount available to a GAS for its expenses (think it as a sort of "virtual wallet"); supplier payments draw from the GAS' cash
- `/expenses/suppliers/<supplier UID>` is used to record payments made from the GAS to a given supplier

::

      . ROOT (/)
      |----------- cash [A]
      |
      +----------- members [P,A]+
      |				|
      |				+--- <UID member #1>  [A]
      |		      		| ..
      |		      		+--- <UID member #n>  [A]
      |
      +----------- incomes [P,I]+
      |				|
      |			        +--- recharges [I] 
      |				|     
      |			        +---  fees [I]
      |
      |
      +----------- expenses [P,E]+
				 |
      			         +--- suppliers [P, E] +
				      		       |
      				     	       	       +--- <UID supplier #1>  [E]
						       | ..
      		      				       +--- <UID supplier #n>  [E]

    

Suppliers
---------
From an accounting point of view, a supplier-like subject can be abstracted as:
* an asset-type account (*wallet*), (virtually) containing supplier-owned money originating from the DES's financial circuit (currently, purchases made by GASs, but one may also envision supplier-to-supplier economic exchanges)
* an income-type hierarchy of accounts recording payments made by GASs having subscribed solidal pacts with the supplier itself

::

      . ROOT (/)
      |----------- wallet [A]
      |
      +----------- incomes [P,I]+
				 |
      			         +--- gas [P, I] +
				      	      	 |
      				     	       	 +--- <UID gas #1>  [P, I]
						 | 			  
						 |  			  
						 | ..			  
						 | 			  
						 | 
						 | 
      		      				 +--- <UID gas #n>  [P, I]
						 			  
						  			 


Common transactions
===================

Person <--> GAS
---------------

GAS <--> GAS
------------

GAS <--> Supplier
-----------------


.. _django-simple-accounting: https://github.com/seldon/django-simple-accounting

.. [1] By setting the variable ``ACCOUNT_PATH_SEPARATOR`` in ``settings.py`` (default: `/`)
