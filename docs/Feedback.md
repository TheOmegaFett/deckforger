# Feedback Log for Project Development

This document tracks the feedback received throughout the planning and development of the project, how it was implemented, and its outcomes.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Feedback Stages](#feedback-stages)
3. [Summary of Changes](#summary-of-changes)
4. [Reflection](#reflection)

---

## Introduction

Feedback played a critical role in improving the quality, functionality, and performance of the application. This log provides a detailed overview of feedback received at various stages, the actions taken to address it, and the outcomes achieved.

---

## Feedback Stages

| **Stage**            | **Source**   | **Feedback**                           | **Action Taken**                                 | **Outcome**                                     |
| -------------------- | ------------ | -------------------------------------- | ------------------------------------------------ | ----------------------------------------------- |
| **Initial Planning** | Peer Review  | Reduce redundancy in the database/ERD. | Updated ERD to include addition entity.          | ERD now accurately represents the data model.   |
| **Testing Phase**    | User Testing | Include full cardset details in API.   | Nested `cardset` relationship using Marshmallow. | Cardset details now show full information.      |
| **Testing Phase**    | User Testing | Include search functionality in API.   | Added search endpoint for cards.                 | Cards details now searchable.                   |
| **Post-Testing**     | Self-Review  | Improve API error handling.            | Added proper error responses with status codes.  | Clearer error messaging for invalid requests.   |
| **Testing Phase II** | User Testing | Need TCG Live format compatibility     | Added import/export endpoints for TCG Live       | Users can now directly import/export deck lists |

---

## Screenshots and Evidence

### 1. **ERD Improvement**

**Before Feedback:**  
_Redundency in entity-relationship diagram (ERD)._  
![Before ERD](./screenshots/erd_plan_before.png)

**After Feedback:**  
_Updated ERD to include all entities and relationships._  
![Updated ERD](./screenshots/erd_plan.png)

---

### 2. **Cardset Serialization Fix**

**Before Feedback:**  
Cards only displayed the `set_id`.

{

"id": 1,
"name": "Fezandipiti EX",
"cardtype": {
"id": 16,
"name": "Dark"
},
"cardset_id": 1
}
After Feedback:
Cardset now shows full details.

{
"id": 1,
"name": "Fezandipiti EX",
"cardtype": {
"id": 16,
"name": "Dark"
},
"cardset": {
"id": 1,

"name": "Shrouded Fable",
"release_date": "2024-06-01"
}
}

---

### 3. **Addition of card search feature**

**Before Feedback:**  
Cards only could only be retrieved by their ID.

**After Feedback:**
Cards are now searchable by name, type, and cardset.

@card_controller.route('/search', methods=['GET'])
def search_cards():

"""
Search for Pokemon cards using filters.

Search Parameters:
name (str, optional): Card name to search for
type (str, optional): Card type to filter by
cardset_id (int, optional): Set ID to filter by

Returns:
200: List of matching cards
"""
stmt = db.select(Card)

if name := request.args.get('name'):
stmt = stmt.filter(Card.name.ilike(f'%{name}%'))
if card_type := request.args.get('cardtype'):
stmt = stmt.filter(Card.cardtype.ilike(f'%{card_type}%'))
if cardset_id := request.args.get('cardset_id'):
stmt = stmt.filter(Card.cardset_id == cardset_id)

cards = db.session.scalars(stmt).all()
return cards_schema.jsonify(cards), 200

### 3. **Addition of TCG Live Import/Export**

**Before Feedback:**  
Decks could only be created through manual API calls.

**After Feedback:**
Decks can be imported directly from and exported to TCG Live format:

```python
@deck_controller.route('/import/<deck_name>/<int:format_id>/<int:deckbox_id>', methods=['POST'])

@deck__controller.route('/export/<int:deck_id>', methods=['GET'])
```

---

## Summary of Changes

By implementing feedback at multiple stages during the project, the following improvements were made:

- Improved ERD: All entities and relationships are now correctly represented.
- Fixed API Serialization: Nested relationships now display full details.
- Cards are now searchable by name, type, and cardset.
- Enhanced Error Handling: Improved user experience through clear error responses.
- TCG Live Import/Export: Users can now directly import/export deck lists.

---

## Reflection

Feedback throughout the project was invaluable in identifying areas for improvement and ensuring the application met its goals. By addressing feedback from peers and users at multiple stages, the project evolved into a robust and optimized application.

This process highlighted the importance of:

- Collaborative review for early issue identification.
- Continuous testing and user feedback during development.
- Iterative improvements based on constructive feedback.

---

## Acknowledgments

- Peer reviewers and mentors for their insights during planning and development.
- Testers for identifying functional and user experience issues.
- Self-review sessions for spotting performance optimizations.

---
