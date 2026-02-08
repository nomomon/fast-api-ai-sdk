'use client';

import { Github, LayoutDashboard, MessageSquare, Plus } from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import type * as React from 'react';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@/components/ui/sidebar';
import { NavUser } from '@/components/user/nav-user';
import { APP_SHORT_NAME, ICON_PATHS } from '@/lib/constants/seo';
import { useNewChat } from '@/lib/contexts/new-chat-context';
import { Separator } from './ui/separator';

const GITHUB_URL = 'https://github.com/nomomon/fast-api-ai-sdk';

const navItems = [
  { title: 'Chat', href: '/', icon: MessageSquare },
  { title: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
] as const;

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname();
  const router = useRouter();
  const { requestNewChat } = useNewChat();

  const handleNewChat = () => {
    if (pathname === '/') {
      requestNewChat();
    } else {
      router.push('/');
    }
  };

  return (
    <Sidebar variant="floating" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/">
                <Image
                  src={ICON_PATHS.svg}
                  alt=""
                  width={32}
                  height={32}
                  className="size-8 aspect-square object-cover rounded-md"
                />
                <div className="flex flex-col gap-0.5 leading-none">
                  <span className="font-medium">{APP_SHORT_NAME}</span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton onClick={handleNewChat} tooltip="New chat">
                <Plus className="size-4" />
                <span>New chat</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
            <Separator className="my-2" />
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild isActive={isActive} tooltip={item.title}>
                    <Link href={item.href}>
                      <Icon className="size-4" />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              );
            })}
            <Separator className="my-2" />
            <SidebarMenuItem>
              <SidebarMenuButton asChild tooltip="GitHub repository">
                <a
                  href={GITHUB_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Open repository on GitHub"
                >
                  <Github className="size-4" />
                  <span>GitHub</span>
                </a>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu></SidebarMenu>
        <NavUser />
      </SidebarFooter>
    </Sidebar>
  );
}
