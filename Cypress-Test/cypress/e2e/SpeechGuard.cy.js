describe('SpeechGuard Check', () => {

  // Assertions
  it('Validate Content', () => {

      // Visit Website
      cy.visit('http://127.0.0.1:5000/')
      
      // Check heading
      cy.get('h1').should('have.text', 'SpeechGuard ');

      // Check input field
      cy.get('#input_link').should('exist');

      // Check submit button
      cy.get('#submitBtn').should('have.text', 'Check');

      // Check clear button
      cy.get('#clearData').should('have.text', 'Clear Data');

      // Check iFrame
      cy.get('iframe').should('exist');
  })

  // Input Data
  it('Input Data', () => {

      // Visit Website
      cy.visit('http://127.0.0.1:5000/')

      // Input URL
      cy.get('#input_link').type('https://www.youtube.com/watch?v=MxEgpEoESiU')

      // Click check Button
      cy.get('#submitBtn').click();

      // Check output is visible
      cy.get('.result-title').eq(0).should('exist');

      cy.get('.result-title').eq(1).should('exist');

      cy.get('.result-title').eq(2).should('exist');

      cy.get('.result-title').eq(3).should('exist');

      cy.get('.result-title').eq(4).should('exist');

      cy.get('.result-title').eq(5).should('exist');

      // Check iFrame src
      cy.get('iframe').should('have.attr', 'src', 'https://www.youtube.com/embed/MxEgpEoESiU');

      // Click clear Data
      cy.get('#clearData').click();

      // Check message
      cy.contains('Data cleared successfully.').should('exist');

      // Click clear Data again
      cy.get('#clearData').click();

      // Check message
      cy.contains('Data not found.').should('exist');

      // Data should be cleared
      cy.get('#input_link').should('have.value', '');

      cy.get('.result-title').eq(0).should('have.value', '');

      cy.get('.result-title').eq(1).should('have.value', '');

      cy.get('.result-title').eq(2).should('have.value', '');

      cy.get('.result-title').eq(3).should('have.value', '');

      cy.get('.result-title').eq(4).should('have.value', '');

      cy.get('.result-title').eq(5).should('have.value', '');

  })
})