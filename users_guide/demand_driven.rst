.. _demand_driven:

Demand Driven Documentation
===========================

Facets is a large software package and will eventually have a correspondingly
extensive documentation set to match. But until that day arrives, we'd like
to prioritize the creation of documentation using a *demand driven* approach.

That is, if there are portions of Facets that you would like to see documented
(or documented better), please let the author know. Whatever user feedback is
received will be recorded in the :ref:`document_to_do` list.

Documentation items in the *to do* list will be handled as follows:

* Items at the top of the list will be documented before items lower on the
  list.
* Each item will have a request count and id associated with it.
* New user submitted items will be added to the end of the list with a request
  count of one and a new, unique id.
* Duplicate requests for the same item id (by different users) will increase the
  item's request count by one.
* When an item's request count increases, it will move up the list to be just
  above every other item with a smaller request count.
* To avoid *spamming* the list, user's will only be able to *vote* for one item
  submitted by another user once per 24 hour period.
* The package author reserves the right to add new items to the list. In such
  cases, the new item will be added to the end of list with a request count of
  zero. That is, it will remain below all user submitted requests until one or
  more users *vote* it up. This is to allow the package author to suggest topics
  that users may not be aware of.

The following additional rules for maintaining the list will also apply:

* If an incoming documentation request is too vague or broad (e.g. *document
  the Facets UI system*), it will be added to the end of the
  :ref:`pending_documentation` list, along with the user's name and date,
  awaiting further refinement or clarification by the submitting user.
  Additional comments explaining what needs to be clarified or refined may also
  be added as needed.
* If the submitting user provides a valid follow-up clarification, the resulting
  item will be moved from the *pending* to the *to do* list as described above.
* If a follow-up clarification is still too vague or broad, the clarification
  will be added to or replace the original item on the *pending* list, where it
  will continue to await additional clarification.
* If an item remains on the *pending* list for a long period of time (say one
  month) without any further clarification being provided, it will be deemed
  *dead* and removed from the *pending* list.

The :ref:`ui_demo` is considered part of the Facets documentation, so requests
for writing a demo illustrating a particular set of Facets features can be
included in the *to do* list.
