---

# **Project Planning Document**  
**Project Title:** Deckforger  
**Owner/Lead Developer:** Shane  

---

## **1. Project Overview**

This project focuses on building a RESTful API to manage Pokémon TCG cards, decks, and deckboxes. It includes functionality for:

- **Card Management**: CRUD operations for individual cards.
- **Deck Management**: Create, update, validate, and organize decks.
- **Deckbox Management**: Group decks into deckboxes with add/remove operations.
- **Set and Format Management**: Manage Pokémon TCG sets and deck formats.
- **Administrative Operations**: Database health checks, cleanup, and management.

---

## **2. Objectives**

1. Build and document a RESTful API using Flask and PostgreSQL.
2. Provide endpoints for managing cards, decks, and deckboxes.
3. Enable deck validation to ensure compliance with TCG rules (Standard/Extended).
4. Include administrative operations like seeding, cleanup, and health checks.
5. Deploy the API to Render (backend) and Neon (database).
6. Test the API using **Insomnia** and **curl**.

---

## **3. Key Features**

| **Feature**          | **Description**                                      | **Endpoints**                                  |
| -------------------- | ---------------------------------------------------- | ---------------------------------------------- |
| Card Management      | Manage Pokémon cards (CRUD).                         | `/api/cards/`                                  |
| Deck Management      | Create, update, validate, and manage decks.          | `/api/decks/`, `/api/decks/validate/<id>`      |
| Deckbox Management   | Group decks into deckboxes, manage relations.        | `/api/deckboxes/`, `/api/deckboxes/<id>/decks` |
| Set Management       | Manage Pokémon TCG sets (CRUD).                      | `/api/cardsets/`                               |
| Format Management    | Manage formats like Standard or Extended.            | `/api/formats/`                                |
| Administrative Tasks | Database setup, health checks, cleanup, and seeding. | `/run/*`, `/health`                            |

---

## **4. Technical Stack**

| **Component**    | **Technology**        |
| ---------------- | --------------------- |
| Backend API      | Flask                 |
| Database         | PostgreSQL (Neon)     |
| Hosting          | Render                |
| Version Control  | GitHub                |
| API Testing      | Insomnia / curl       |
| Validation Logic | Custom (Flask models) |
| Documentation    | Sphinx                |

---

## **5. Endpoints Summary**

| **Resource**            | **Path**                              | **Methods**       | **Description**                          |
| ----------------------- | ------------------------------------- | ----------------- | ---------------------------------------- |
| **Health Check**        | `/health`                             | GET               | Verify API health status.                |
| **Database Management** | `/run/create` `/run/drop` `/run/seed` | POST              | Manage database tables.                  |
| **Decks**               | `/api/decks/`                         | POST              | Create a deck.                           |
|                         | `/api/decks/validate/<id>`            | GET               | Validate deck rules.                     |
|                         | `/api/decks/<id>`                     | PUT               | Update a deck.                           |
| **Deckboxes**           | `/api/deckboxes/`                     | POST, GET         | CRUD operations for deckboxes.           |
|                         | `/api/deckboxes/<id>/decks`           | GET, POST, DELETE | Manage decks in a deckbox.               |
| **Cards**               | `/api/cards/`                         | POST, GET         | CRUD operations for cards.               |
|                         | `/api/cards/<id>`                     | GET, PUT, DELETE  | Fetch, update, or delete a card.         |
| **Sets**                | `/api/cardsets/`                      | POST, GET         | CRUD operations for card sets.           |
| **Formats**             | `/api/formats/`                       | POST, GET         | Manage deck formats (Standard/Extended). |

---

## **6. Timeline (1 Week)**

| **Phase**                | **Tasks**                                       | **Duration** |
| ------------------------ | ----------------------------------------------- | ------------ |
| **Day 1: Setup**         | Project structure, database schema.             | 1 Day        |
| **Day 2 & 3: Endpoints** | Implement CRUD for cards, decks, and deckboxes. | 2 Days       |
| **Day 4: Validation**    | Add deck validation logic and API testing.      | 1 Day        |
| **Day 5: Deployment**    | Deploy to Render and Neon, test all routes.     | 1 Day        |

---

## **7. Risks and Mitigation**

| **Risk**                | **Mitigation Strategy**                        |
| ----------------------- | ---------------------------------------------- |
| Data Integrity Issues   | Add thorough validation and test coverage.     |
| Deployment Delays       | Incremental deployment with environment tests. |
| Performance Bottlenecks | Optimize database queries and caching.         |

---

## **8. Next Steps**

1. Set up the Flask project folder and virtual environment.
2. Initialize PostgreSQL schema on Neon.
3. Implement basic CRUD for `/api/cards` and `/api/decks`.
4. Develop validation logic for decks.
5. Test endpoints using **Insomnia** and **curl**.

---
