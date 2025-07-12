"use client";

import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import React, { useState, useEffect } from "react";
import { toast } from "sonner";
import { ThemeToggle } from "@/components/theme-toggle";

export function Chat() {
  const chatId = "001";
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>();

  const [isClient, setIsClient] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  if (!input.trim()) return;

  const userMessage = { id: Date.now(), role: "user", content: input };
  setMessages((prev) => [...prev, userMessage]);
  setIsLoading(true);
  setInput("");

  try {
    // A única mudança é na linha 'body' abaixo
    const res = await fetch("http://127.0.0.1:8000/api/v1/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: [userMessage] }),
    });

    if (!res.ok) {
        const errorBody = await res.text();
        console.error("Falha na API:", res.status, errorBody);
        throw new Error("Failed to send message");
    }

    // Como o backend agora retorna PlainText, precisamos ler a resposta assim
    
    const responseText = await res.text();
    console.log("Resposta do backend:", responseText);
    console.log("Resposta do backend:", res);
    const botMessage = {
      id: Date.now() + 1,
      role: "assistant",
      content: responseText, // <-- Usar o texto da resposta
    };
    setMessages((prev) => [...prev, botMessage]);

  } catch (error: any) {
    setMessages((prev) => [
      ...prev,
      { id: Date.now() + 2, role: "assistant", content: "Desculpe, ocorreu um erro." },
    ]);
  } finally {
    setIsLoading(false);
  }
};
  const handleFileSubmit = async (file: File) => {
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: "Analisando imagem...",
      imageUrl: URL.createObjectURL(file) 
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/chat/upload-document", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Failed to upload file");

      const data = await res.json();
      const botMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.response,
      };
      setMessages((prev) => [...prev, botMessage]);

    } catch (error) {
      setMessages(prev => prev.map(m => 
          m.id === userMessage.id ? { ...m, content: "Erro ao analisar imagem." } : m
      ));
    } finally {
      setIsLoading(false);
    }
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
          onFileSelect={handleFileSubmit}
        />
      </form>
    </div>
  );
}
