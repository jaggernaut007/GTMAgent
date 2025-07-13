import React from 'react';
import styled from 'styled-components';
import Chatbot from './components/Chatbot/Chatbot';

const AppContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
`;

function App() {
  return (
    <AppContainer>
      <Chatbot />
    </AppContainer>
  );
}

export default App;
