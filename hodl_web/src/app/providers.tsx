'use client';

import { ReactNode } from 'react';

interface ProvidersProps {
  children: ReactNode;
}

function Providers({ children }: ProvidersProps) {
  // 这里可以添加未来需要的全局提供者组件
  // 例如：ThemeProvider, WalletProvider等
  return (
    <>
      {children}
    </>
  );
};

export default Providers;
