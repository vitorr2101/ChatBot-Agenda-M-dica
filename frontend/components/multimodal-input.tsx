"use client";

import type { ChatRequestOptions, CreateMessage, Message } from "ai";
import { motion } from "framer-motion";
import type React from "react";
import {
  useRef,
  useEffect,
  useCallback,
  type Dispatch,
  type SetStateAction,
} from "react";
import { toast } from "sonner";
import { useLocalStorage, useWindowSize } from "usehooks-ts";

import { cn, sanitizeUIMessages } from "@/lib/utils";
import { PreviewAttachment } from "@/components/preview-attachment";

import { ArrowUpIcon, StopIcon, PaperclipIcon, UploadIcon } from "./icons";
import { Button } from "./ui/button";
import { Textarea } from "./ui/textarea";

const suggestedActions = [
  {
    title: "Agendar uma consulta",
    label: "com um clínico geral.",
    action: "Gostaria de agendar uma consulta com um clínico geral.",
  },
  {
    title: "Verificar resultados de exames",
    label: "de sangue e imagem.",
    action: "Gostaria de verificar os resultados dos meus últimos exames.",
  },
  {
    title: "Especialidades médicas",
    label: "disponíveis na clínica.",
    action: "Quais são as especialidades médicas disponíveis na clínica?",
  },
  {
    title: "Cancelar ou remarcar",
    label: "um agendamento.",
    action: "Preciso cancelar ou remarcar um agendamento.",
  },
];

export function MultimodalInput({
  chatId,
  input,
  setInput,
  isLoading,
  stop,
  messages,
  setMessages,
  append,
  handleSubmit,
  className,
  onFileSelect,
  selectedFiles = [],
  onFileRemove,
}: {
  chatId: string;
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  stop: () => void;
  messages: Array<Message>;
  setMessages: Dispatch<SetStateAction<Array<Message>>>;
  append: (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions,
  ) => Promise<string | null | undefined>;
  handleSubmit: (
    event?: {
      preventDefault?: () => void;
    },
    chatRequestOptions?: ChatRequestOptions,
  ) => void;
  className?: string;
  onFileSelect: (file: File) => void;
  selectedFiles?: File[];
  onFileRemove?: (index: number) => void;
}) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const { width } = useWindowSize();

  useEffect(() => {
    if (textareaRef.current) {
      adjustHeight();
    }
  }, []);

  const adjustHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight + 2}px`;
    }
  };

  const [localStorageInput, setLocalStorageInput] = useLocalStorage(
    "input",
    "",
  );

  useEffect(() => {
    if (textareaRef.current) {
      const domValue = textareaRef.current.value;
      const finalValue = domValue || localStorageInput || "";
      setInput(finalValue);
      adjustHeight();
    }
  }, [localStorageInput, setInput]);

  useEffect(() => {
    setLocalStorageInput(input);
  }, [input, setLocalStorageInput]);

  const handleInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
    adjustHeight();
  };

  const submitForm = useCallback(() => {
    handleSubmit(undefined, {});
    setLocalStorageInput("");

    if (width && width > 768) {
      textareaRef.current?.focus();
    }
  }, [handleSubmit, setLocalStorageInput, width]);

  // Nova função para lidar com a seleção de arquivos (múltiplos)
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      for (let i = 0; i < files.length; i++) {
        onFileSelect(files[i]);
      }
    }
    // Limpar o input para permitir selecionar o mesmo arquivo novamente
    if (event.target) {
      event.target.value = '';
    }
  };

  // Funções para drag and drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files) {
      for (let i = 0; i < files.length; i++) {
        onFileSelect(files[i]);
      }
    }
  };

  // Função para renderizar preview usando o componente existente
  const renderFilePreview = (file: File, index: number) => {
    const fileUrl = URL.createObjectURL(file);

    return (
      <div key={`${file.name}-${index}`} className="flex-shrink-0">
        <PreviewAttachment
          attachment={{
            name: file.name,
            url: fileUrl,
            contentType: file.type,
          }}
          showRemoveButton={!!onFileRemove}
          onRemove={() => onFileRemove?.(index)}
        />
      </div>
    );
  };

  return (
    <div className="relative w-full flex flex-col gap-4">
      {messages.length === 0 && (
        <div className="grid sm:grid-cols-2 gap-2 w-full">
          {suggestedActions.map((suggestedAction, index) => (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ delay: 0.05 * index }}
              key={`suggested-action-${suggestedAction.title}-${index}`}
              className={index > 1 ? "hidden sm:block" : "block"}
            >
              <Button
                variant="ghost"
                onClick={async () => {
                  setInput(suggestedAction.action);
                  setTimeout(() => submitForm(), 100);
                }}
                className="text-left border rounded-xl px-4 py-3.5 text-sm flex-1 gap-1 sm:flex-col w-full h-auto justify-start items-start"
              >
                <span className="font-medium">{suggestedAction.title}</span>
                <span className="text-muted-foreground">
                  {suggestedAction.label}
                </span>
              </Button>
            </motion.div>
          ))}
        </div>
      )}

      {/* Container principal que engloba preview e input - AGORA É A DROPZONE */}
      <div 
        className="bg-muted/30 rounded-2xl flex flex-col border-2 border-dashed border-muted-foreground/15 transition-colors hover:border-muted-foreground/30 hover:bg-muted/50"
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {/* Input de arquivo oculto */}
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          onChange={handleFileChange}
          multiple
          accept="image/*,application/pdf,.pdf,.doc,.docx,.txt"
        />

        {/* Área de Preview dos Arquivos */}
        {selectedFiles && selectedFiles.length > 0 && (
          <div className="p-3">
            <div className="flex gap-3 overflow-x-auto items-center">
              {selectedFiles.map((file, index) => renderFilePreview(file, index))}
              {/* Botão simples para adicionar mais arquivos */}
              <div className="flex-shrink-0 w-20 aspect-video flex items-center justify-center">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-primary/50 hover:text-primary/75 transition-colors cursor-pointer rounded-full hover:bg-muted/50"
                  disabled={isLoading}
                  aria-label="Adicionar mais arquivos"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Container para o Textarea e botões */}
        <div className="relative flex items-center p-2">
          {/* Ícone de upload centralizado - apenas quando não há texto nem arquivos */}
          {!input && (!selectedFiles || selectedFiles.length === 0) && (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="absolute inset-0 flex items-center justify-center cursor-pointer text-primary/50 hover:text-primary/75 transition-colors z-5 pointer-events-none"
            >
              <div className="pointer-events-auto">
                <UploadIcon size={20} />
              </div>
            </div>
          )}

          <Textarea
            ref={textareaRef}
            placeholder="Digite sua mensagem..."
            value={input}
            onChange={handleInput}
            className={cn(
              "min-h-[50px] max-h-[calc(75dvh)] overflow-hidden resize-none rounded-lg !text-base bg-transparent border-0 pl-4 pr-12 focus:ring-0 focus:ring-offset-0 focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0",
              className,
            )}
            rows={2}
            autoFocus
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();

                if (isLoading) {
                  toast.error("Please wait for the model to finish its response!");
                } else {
                  submitForm();
                }
              }
            }}
          />

          {isLoading ? (
            <Button
              className="rounded-full p-1.5 h-fit absolute bottom-4 right-4 m-0.5 border dark:border-zinc-600"
              onClick={(event) => {
                event.preventDefault();
                stop();
                setMessages((messages) => sanitizeUIMessages(messages));
              }}
            >
              <StopIcon size={14} />
            </Button>
          ) : (
            <Button
              className="rounded-full p-1.5 h-fit absolute bottom-4 right-4 m-0.5 border dark:border-zinc-600"
              onClick={(event) => {
                event.preventDefault();
                submitForm();
              }}
              disabled={input.length === 0 && (!selectedFiles || selectedFiles.length === 0)}
            >
              <ArrowUpIcon size={14} />
            </Button>
          )}
        </div>
      </div>
  </div>
  );
}
