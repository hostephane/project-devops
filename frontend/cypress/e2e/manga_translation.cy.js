// frontend/cypress/e2e/manga_translation.cy.js

describe('Manga Translation App E2E Tests', () => {
  beforeEach(() => {
    cy.visit('http://localhost:5173');  // adapte ici si URL prod ou autre
  });

  it('Uploads an image and fetches translations', () => {
    cy.get('input[type="file"]').attachFile('sample_image.jpg');
    cy.get('button').contains('Traduire').click();
    cy.contains('Chargement...');
    cy.get('.bubble-list li', { timeout: 30000 }).should('have.length.greaterThan', 0);
  });

  it('Displays error when uploading an invalid file', () => {
    cy.get('input[type="file"]').attachFile({
      fileContent: 'not an image',
      fileName: 'invalid.txt',
      mimeType: 'text/plain',
    });
    cy.get('button').contains('Traduire').click();
    cy.contains('Erreur', { timeout: 10000 }).should('be.visible');
  });

  it('Button "Traduire" disabled when no file is selected', () => {
    cy.get('input[type="file"]').should('have.value', '');
    cy.get('button').contains('Traduire').should('not.be.disabled');
    // À adapter si tu désactives le bouton dans le frontend avec disabled={!file || loading}
  });
});
