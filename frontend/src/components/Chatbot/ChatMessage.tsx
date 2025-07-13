import React, { ReactNode } from 'react';
import styled from 'styled-components';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;
  children?: ReactNode;
}

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: 70%;
  padding: 10px 15px;
  margin: 5px 0;
  border-radius: 18px;
  background: ${props => props.isUser ? '#007bff' : '#e9ecef'};
  color: ${props => props.isUser ? 'white' : 'black'};
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  word-wrap: break-word;
  position: relative;
  min-width: 100px;
`;

const MessageContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 0 10px;
  margin: 5px 0;
`;

const Timestamp = styled.div<{ isUser: boolean }>`
  font-size: 0.7rem;
  color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.7)' : '#6c757d'};
  text-align: ${props => props.isUser ? 'right' : 'left'};
  margin-top: 2px;
  padding: 0 5px;
`;

const formatTime = (date?: Date) => {
  if (!date) return '';
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const ChatMessage: React.FC<ChatMessageProps> = ({ message, isUser, timestamp, children }) => {
  return (
    <MessageContainer>
      <MessageBubble isUser={isUser}>
        {children || message}
        {timestamp && (
          <Timestamp isUser={isUser}>
            {formatTime(timestamp)}
          </Timestamp>
        )}
      </MessageBubble>
    </MessageContainer>
  );
};

export default ChatMessage;
