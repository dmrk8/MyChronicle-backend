import { useEffect } from 'react';

interface UseInfiniteScrollProps {
  callback: () => void; //called when you need more data
  isLoading: boolean;
  hasNextPage: boolean;
  container?: HTMLElement | null; //work on the element provided
}

export function UseInfiniteScroll({
  callback,
  isLoading,
  hasNextPage,
  container,
}: UseInfiniteScrollProps) {
  useEffect(() => {
    if (isLoading || !hasNextPage) return;

    const target = container || window;
    const handleScroll = () => {
      const scrollPosition = container
        ? container.scrollTop + container.clientHeight
        : window.innerHeight + window.scrollY;
      const bottomPosition = container
        ? container.scrollHeight
        : document.body.offsetHeight;

      console.log(
        'Scroll position:',
        scrollPosition,
        'Bottom position:',
        bottomPosition
      );

      if (scrollPosition >= bottomPosition - 200 && !isLoading && hasNextPage) {
        console.log('Callback triggered');
        callback();
      }
    };

    target.addEventListener('scroll', handleScroll);
    return () => {
      target.removeEventListener('scroll', handleScroll);
    };
  }, [callback, isLoading, hasNextPage, container]);
}
