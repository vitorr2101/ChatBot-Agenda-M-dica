import { motion } from "framer-motion";

import { Icons } from "@/components/icons";

export const Overview = () => {
  return (
    <motion.div
      key="overview"
      className="max-w-3xl mx-auto md:mt-20"
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ delay: 0.5 }}
    >
      <div className="text-center rounded-lg p-10 flex flex-col items-center">
        <div className="mb-4">
          <Icons.logo className="w-16 h-16 text-primary" />
        </div>
        <h1
          className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"
        >
          Ampla Saúde
        </h1>
        <p className="text-lg text-foreground mt-6 max-w-md leading-relaxed">
          Cuidar da sua saúde ficou mais simples.
        </p>
        <p className="text-base text-muted-foreground mt-2 max-w-md leading-relaxed">
          Olá! Sou sua assistente virtual da Ampla Saúde. Estou aqui para te ajudar
          a agendar consultas e exames com todo o conforto e segurança.
        </p>
        <p className="text-base font-medium text-foreground mt-8">
          O que você gostaria de fazer hoje?
        </p>
      </div>
    </motion.div>
  );
};
