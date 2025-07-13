import React, { ReactNode } from 'react';
import styled from 'styled-components';

interface ChatMessageProps {
  message: string;
  isUser: boolean;
  timestamp?: Date;
  children?: ReactNode;
}

const MessageBubble = styled.div<{ isUser: boolean }>`
  max-width: 80%;
  padding: 14px 18px;
  margin: 8px 0;
  border-radius: 18px;
  background: ${props => props.isUser ? '#007bff' : '#f0f2f5'};
  color: ${props => props.isUser ? 'white' : '#1c1e21'};
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  word-wrap: break-word;
  position: relative;
  min-width: 100px;
  line-height: 1.6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  white-space: pre-wrap;
`;

const MessageContainer = styled.div<{ isUser: boolean }>`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 0 16px;
  margin: 4px 0;
  font-size: 0.95rem;
  text-align: ${props => props.isUser ? 'right' : 'left'};
  margin-top: ${props => props.isUser ? '8px' : '4px'};
  margin-bottom: ${props => props.isUser ? '4px' : '8px'};
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
    <MessageContainer isUser={isUser}>
      <MessageBubble isUser={isUser}>
        {children || (
          <div style={{
            fontSize: '15px',
            lineHeight: '1.6',
            color: isUser ? 'white' : '#1c1e21',
            fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
          }}>
            {message}
          </div>
        )}
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
