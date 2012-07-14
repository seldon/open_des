Subjects
========

GASes
-----

A GAS is a group of other subjects, called *GAS members*.  A member of a given GAS may be either a person or another
GAS.  This way, we are able to model a hierarchy of GASes, if needed.  We'll call a GAS which counts only people as its
members a *first-order GAS* (or, simply, a GAS), while if a GAS includes other GASes among its members, we call it *a
second-order GAS* or a *Retina* [#]_.

Data describing GAS memberships is stored by the ``IsGasMember`` model.






.. rubric:: Footnotes

.. [#]: Note that, by definition, a retina may feature both people and other GASes among its members.
 
