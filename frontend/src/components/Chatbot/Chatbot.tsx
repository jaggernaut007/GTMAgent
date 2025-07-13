import React, { useState, useRef, useEffect } from 'react';
import styled, { keyframes } from 'styled-components';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { sendMessage, checkHealth } from '../../utils/api';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  isLoading?: boolean;
  error?: string;
}

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 800px;
  height: 600px;
  margin: 20px auto;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
`;

const Header = styled.div`
  padding: 15px 20px;
  background: #007bff;
  color: white;
  font-size: 1.2rem;
  font-weight: 500;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const StatusIndicator = styled.span<{ $isOnline: boolean }>`
  height: 10px;
  width: 10px;
  background-color: ${props => props.$isOnline ? '#28a745' : '#dc3545'};
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
`;

const WelcomeMessage = styled.div`
  text-align: center;
  color: #6c757d;
  margin-top: 20px;
  font-style: italic;
`;

const LoadingDots = styled.div`
  display: inline-flex;
  align-items: center;
  height: 100%;
  padding: 0 15px;
`;

const bounce = keyframes`
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
`;

const Dot = styled.span`
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #6c757d;
  margin: 0 2px;
  animation: ${bounce} 1.4s infinite ease-in-out both;
  
  &:nth-child(1) { animation-delay: -0.32s; }
  &:nth-child(2) { animation-delay: -0.16s; }
`;

const ErrorMessage = styled.div`
  color: #dc3545;
  font-size: 0.9rem;
  margin-top: 5px;
  font-style: italic;
`;

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isOnline, setIsOnline] = useState<boolean>(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check backend health on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      const healthy = await checkHealth();
      setIsOnline(healthy);
      
      if (healthy) {
        setMessages([{
          id: 1,
          text: "Hello! I'm your Startup Bakery assistant. How can I help you today?",
          isUser: false,
          timestamp: new Date()
        }]);
      } else {
        setMessages([{
          id: 1,
          text: "Unable to connect to the server. Please make sure the backend is running.",
          isUser: false,
          error: 'Connection error',
          timestamp: new Date()
        }]);
      }
    };

    checkBackendHealth();
  }, []);

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || !isOnline || isLoading) return;

    
    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      text: message,
      isUser: true,
      timestamp: new Date()
    };
    
    // Add loading indicator with a unique ID
    const loadingId = Date.now() + 1;
    const loadingMessage: Message = {
      id: loadingId,
      text: '...',
      isUser: false,
      isLoading: true,
      timestamp: new Date()
    };
    
    // Add both messages at once to avoid multiple re-renders
    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setIsLoading(true);
    try {
      // Send message to backend
      const response = await sendMessage(message);
      
      if (response.error) {
        throw new Error(response.error);
      }
      
      // Update loading message with bot response
      setMessages(prev => {
        return prev.map(msg => 
          msg.id === loadingId 
            ? {
                ...msg,
                text: response.data?.response || "I'm sorry, I couldn't process your request.",
                isLoading: false,
                timestamp: new Date()
              }
            : msg
        );
      });
    } catch (error) {
      console.error('Error in handleSendMessage:', error);
      
      // Update loading message with error
      setMessages(prev => {
        return prev.map(msg => 
          msg.id === loadingId
            ? {
                ...msg,
                text: "I'm having trouble connecting to the server. Please try again later.",
                error: error instanceof Error ? error.message : 'Connection error',
                isLoading: false,
                timestamp: new Date()
              }
            : msg
        );
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const renderMessageContent = (message: Message) => {
    if (message.isLoading) {
      return (
        <LoadingDots>
          <Dot /><Dot /><Dot />
        </LoadingDots>
      );
    }
    
    return (
      <>
        {message.text}
        {message.error && <ErrorMessage>{message.error}</ErrorMessage>}
      </>
    );
  };

  return (
    <ChatContainer>
      <Header>
        <span>Startup Bakery Assistant</span>
        <div>
          <StatusIndicator $isOnline={isOnline} />
          {isOnline ? 'Online' : 'Offline'}
        </div>
      </Header>
      <MessagesContainer>
        {messages.length === 0 ? (
          <WelcomeMessage>
            Connecting to the server...
          </WelcomeMessage>
        ) : (
          messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message.isLoading ? '' : message.text}
              isUser={message.isUser}
              timestamp={message.timestamp}
            >
              {renderMessageContent(message)}
            </ChatMessage>
          ))
        )}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      <ChatInput 
        onSendMessage={handleSendMessage} 
        disabled={isLoading || !isOnline}
      />
    </ChatContainer>
  );
};

export default Chatbot;
