import React, { useState, KeyboardEvent } from 'react';
import styled from 'styled-components';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

interface InputContainerProps {
  $disabled?: boolean;
}

const InputContainer = styled.div<InputContainerProps>`
  display: flex;
  padding: 10px;
  background: #f8f9fa;
  border-top: 1px solid #dee2e6;
  transition: all 0.2s;
  
  ${props => props.$disabled && `
    background-color: #f1f1f1;
    opacity: 0.7;
    cursor: not-allowed;
  `}
`;

const Input = styled.input<{ disabled?: boolean }>`
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  outline: none;
  font-size: 14px;
  transition: all 0.2s;
  background-color: ${props => props.disabled ? '#f1f1f1' : 'white'};
  cursor: ${props => props.disabled ? 'not-allowed' : 'text'};
  
  &:focus {
    border-color: #80bdff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
  
  &::placeholder {
    color: ${props => props.disabled ? '#999' : '#6c757d'};
  }
`;

const SendButton = styled.button<{ disabled?: boolean }>`
  margin-left: 10px;
  padding: 0 20px;
  background: ${props => props.disabled ? '#e9ecef' : '#007bff'};
  color: ${props => props.disabled ? '#6c757d' : 'white'};
  border: none;
  border-radius: 20px;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  font-weight: 500;
  transition: all 0.2s;
  opacity: ${props => props.disabled ? 0.7 : 1};
  
  &:hover {
    background: ${props => props.disabled ? '#e9ecef' : '#0056b3'};
  }
`;

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !disabled) {
      console.log(message)
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <InputContainer $disabled={disabled}>
      <Input
        type="text"
        value={message}
        onChange={(e) => !disabled && setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={disabled ? "Connecting to server..." : "Type a message..."}
        disabled={disabled}
      />
      <SendButton 
        onClick={handleSend}
        disabled={!message.trim() || disabled}
      >
        Send
      </SendButton>
    </InputContainer>
  );
};

export default ChatInput;
