"use client";

import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { PreviewAttachment } from "@/components/preview-attachment";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import React, { useState, useEffect } from "react";
import { ThemeToggle } from "@/components/theme-toggle";

export function Chat() {
  const chatId = "001";
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const [isClient, setIsClient] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim() && selectedFiles.length === 0) return;

    // Criar mensagem do usuário - sem modificar o conteúdo da mensagem original
    const userMessage = { 
      id: Date.now(), 
      role: "user", 
      content: input,
      files: selectedFiles.length > 0 ? selectedFiles.map(f => ({
        name: f.name,
        url: URL.createObjectURL(f)
      })) : undefined
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    
    // Limpar campos após adicionar à lista de mensagens
    const currentInput = input;
    const currentFiles = [...selectedFiles];
    setInput("");
    setSelectedFiles([]);

    try {
      // Usar FormData para enviar texto e arquivos juntos
      const formData = new FormData();
      formData.append('message', currentInput);
      
      // Adicionar todos os arquivos selecionados
      currentFiles.forEach((file) => {
        formData.append('file', file);
      });

      const res = await fetch("http://127.0.0.1:8000/api/v1/chat/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        let errorData;
        try {
          errorData = await res.json();
        } catch {
          errorData = { message: "Erro de resposta inválida" };
        }
        
        const errorMessage = errorData?.detail || errorData?.message || "Erro desconhecido";
        console.error("Falha na API:", res.status, errorMessage);
        throw new Error(`API Error ${res.status}: ${errorMessage}`);
      }

      // A resposta agora é JSON
      const data = await res.json();
      const botMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.response,
      };
      setMessages((prev) => [...prev, botMessage]);

    } catch (error: any) {
      console.error("Erro enviando mensagem:", error?.message || error || "Erro desconhecido");
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + 2, role: "assistant", content: "Desculpe, ocorreu um erro." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };
  const handleFileSelect = (file: File) => {
    // Adicionar novo arquivo à lista existente (não substituir)
    setSelectedFiles(prev => [...prev, file]);
  };

  const removeFile = (indexToRemove: number) => {
    setSelectedFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, messagesEndRef]);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <div className="flex flex-col min-w-0 h-dvh bg-background">
      <div className="absolute top-4 right-4">
        {isClient && <ThemeToggle />}
      </div>
      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 flex-1 overflow-y-scroll pt-4 px-4"
      >
        <div className="mx-auto w-full md:max-w-3xl space-y-6">
          {messages.length === 0 && <Overview />}

          {messages.map((message, index) => (
            <PreviewMessage
              key={message.id}
              chatId={chatId}
              message={message}
              isLoading={isLoading && messages.length - 1 === index}
            />
          ))}

          {isLoading &&
            messages.length > 0 &&
            messages[messages.length - 1].role === "user" && <ThinkingMessage />}
        </div>
        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>

      <form className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl" onSubmit={handleSubmit}>
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={setInput}
          handleSubmit={(
            event?: { preventDefault?: (() => void) | undefined },
            chatRequestOptions?: any
          ) => {
            if (event && event.preventDefault) event.preventDefault();
            handleSubmit({ preventDefault: () => {} } as React.FormEvent<HTMLFormElement>);
          }}
          isLoading={isLoading}
          stop={() => {}}
          messages={messages}
          setMessages={setMessages}
          append={async (msg: any, _chatRequestOptions?: any) => {
            setMessages((prev) => [...prev, msg]);
            return null;
          }}
          onFileSelect={handleFileSelect}
          selectedFiles={selectedFiles}
          onFileRemove={removeFile}
        />
      </form>
    </div>
  );
}
