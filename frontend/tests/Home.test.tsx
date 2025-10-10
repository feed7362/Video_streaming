import {render, screen, waitFor} from "@testing-library/react";
import Home from "../src/pages/Home";
import {vi, describe, it, expect} from "vitest";
import "@testing-library/jest-dom";

vi.mock("@/components/VideoCard", () => ({
    default: ({title}: { title?: string; loading?: boolean }) => (
        <div data-testid="video-card">{title || "Loading..."}</div>
    ),
}));

vi.mock("@/components/infinite-scroll", () => ({
    default: ({children}: { children: React.ReactNode }) => (
        <div data-testid="infinite-scroll">{children}</div>
    ),
}));

vi.mock("react-router-dom", async () => {
    const actual = await vi.importActual<typeof import("react-router-dom")>(
        "react-router-dom"
    );
    return {
        ...actual,
        Link: ({to, children}: { to: string; children: React.ReactNode }) => (
            <a href={to} data-testid="link">
                {children}
            </a>
        ),
    };
});

describe("Home component", () => {
    it("renders loading placeholders first, then loads videos", async () => {
        render(<Home/>);

        // Initially shows loading VideoCards
        const placeholders = screen.getAllByTestId("video-card");
        expect(placeholders.length).toBeGreaterThan(0);
        expect(placeholders[0]).toHaveTextContent("Loading...");

        // Wait for the async setTimeout (1s delay + render time)
        await waitFor(
            () => {
                const videoCards = screen.getAllByTestId("video-card");
                expect(videoCards[0]).toHaveTextContent("Mock Video 1");
            },
            {timeout: 2000}
        );

        // Check InfiniteScroll rendered correctly
        expect(screen.getByTestId("infinite-scroll")).toBeInTheDocument();

        // Check multiple videos rendered
        const videos = screen.getAllByTestId("video-card");
        expect(videos.length).toBeGreaterThan(10);

        // Check links exist and point to correct video URLs
        const links = screen.getAllByTestId("link");
        expect(links[0]).toHaveAttribute("href", expect.stringContaining("/watch?v=video-1"));
    });
});
