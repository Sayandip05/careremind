import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export function AvatarDemo() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-8">
      <div className="flex items-center rounded-full border border-slate-200 bg-white p-1.5 shadow-sm">
        <div className="flex -space-x-2">
          <Avatar className="h-8 w-8 ring-2 ring-white">
            <AvatarImage
              src="https://images.unsplash.com/photo-1599566150163-29194dcaad36?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
              alt="Avatar 01"
            />
            <AvatarFallback>A1</AvatarFallback>
          </Avatar>
          <Avatar className="h-8 w-8 ring-2 ring-white">
            <AvatarImage
              src="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
              alt="Avatar 02"
            />
            <AvatarFallback>A2</AvatarFallback>
          </Avatar>
          <Avatar className="h-8 w-8 ring-2 ring-white">
            <AvatarImage
              src="https://images.unsplash.com/photo-1580489944761-15a19d654956?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
              alt="Avatar 03"
            />
            <AvatarFallback>A3</AvatarFallback>
          </Avatar>
          <Avatar className="h-8 w-8 ring-2 ring-white">
            <AvatarImage
              src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
              alt="Avatar 04"
            />
            <AvatarFallback>A4</AvatarFallback>
          </Avatar>
          <Avatar className="h-8 w-8 ring-2 ring-white">
            <AvatarImage
              src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80"
              alt="Avatar 05"
            />
            <AvatarFallback>A5</AvatarFallback>
          </Avatar>
        </div>
        <p className="px-3 text-sm text-slate-500">
          Trusted by <strong className="font-medium text-slate-900">1K+</strong>{" "}
          doctors.
        </p>
      </div>
    </div>
  );
}
