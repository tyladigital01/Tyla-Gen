"""Tyla-Gen CLI - Command-line interface for interacting with Tyla Gen API."""

import click
import requests
import json
import os
from tabulate import tabulate
from colorama import Fore, Style
from typing import Optional

# Get API URL and key from environment
API_URL = os.getenv("TYLA_API_URL", "http://localhost:8000")
API_KEY = os.getenv("TYLA_API_KEY", "")


def get_headers() -> dict:
    """Get HTTP headers with authentication."""
    if not API_KEY:
        click.echo(f"{Fore.RED}Error: TYLA_API_KEY not set{Style.RESET_ALL}")
        raise click.Abort()
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


@click.group()
def cli():
    """Tyla-Gen: All-in-One AI Server for GitHub Codespaces"""
    pass


@cli.command()
def status():
    """Check server and model status."""
    try:
        click.echo(f"{Fore.CYAN}Checking Tyla-Gen status...{Style.RESET_ALL}")
        
        # Health check
        health_resp = requests.get(f"{API_URL}/health", timeout=5)
        if health_resp.status_code != 200:
            click.echo(f"{Fore.RED}✗ Server not responding{Style.RESET_ALL}")
            return
        
        click.echo(f"{Fore.GREEN}✓ Server is running{Style.RESET_ALL}")
        
        # Status check
        status_resp = requests.get(
            f"{API_URL}/v1/status",
            headers=get_headers(),
            timeout=5
        )
        
        if status_resp.status_code == 200:
            data = status_resp.json()
            
            click.echo(f"\n{Fore.CYAN}Model Status:{Style.RESET_ALL}")
            click.echo(f"  Model: {Fore.YELLOW}{data.get('model', 'unknown')}{Style.RESET_ALL}")
            click.echo(f"  Loaded: {Fore.GREEN if data.get('model_loaded') else Fore.RED}{'Yes' if data.get('model_loaded') else 'No'}{Style.RESET_ALL}")
            click.echo(f"  Engine: {Fore.YELLOW}{data.get('inference_engine', 'unknown')}{Style.RESET_ALL}")
            
            if data.get('hardware'):
                hw = data['hardware']
                click.echo(f"\n{Fore.CYAN}Hardware:{Style.RESET_ALL}")
                click.echo(f"  CPU Cores: {hw.get('cpu_cores')}")
                click.echo(f"  RAM: {hw.get('ram_gb')}GB")
                click.echo(f"  Disk: {hw.get('disk_gb')}GB")
                click.echo(f"  GPU: {'Yes' if hw.get('gpu_available') else 'No'}")
        else:
            click.echo(f"{Fore.RED}Failed to get status: {status_resp.text}{Style.RESET_ALL}")
    
    except requests.exceptions.ConnectionError:
        click.echo(f"{Fore.RED}✗ Cannot connect to Tyla-Gen at {API_URL}{Style.RESET_ALL}")
        click.echo(f"  Set TYLA_API_URL environment variable if using a different address")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
@click.argument("message")
@click.option("--temperature", default=0.7, help="Temperature for generation (0.0-1.0)")
@click.option("--max-tokens", default=512, help="Max tokens to generate")
def chat(message: str, temperature: float, max_tokens: int):
    """Chat with Tyla-Gen using local model."""
    try:
        click.echo(f"{Fore.CYAN}Sending to Tyla-Gen...{Style.RESET_ALL}")
        
        response = requests.post(
            f"{API_URL}/v1/chat/completions",
            headers=get_headers(),
            json={
                "messages": [{"role": "user", "content": message}],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data["choices"][0]["text"] if data.get("choices") else "No response"
            
            click.echo(f"\n{Fore.GREEN}Tyla-Gen:{Style.RESET_ALL}")
            click.echo(result)
            
            if data.get("local_inference"):
                click.echo(f"\n{Fore.CYAN}[Local inference via {data.get('inference_engine', 'unknown')}]{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.RED}Error: {response.status_code} - {response.text}{Style.RESET_ALL}")
    
    except requests.exceptions.Timeout:
        click.echo(f"{Fore.RED}Request timed out - model may be generating or server is busy{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        click.echo(f"{Fore.RED}Cannot connect to Tyla-Gen at {API_URL}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
@click.argument("task")
@click.option("--tools", multiple=True, help="Available tools (e.g., calculator, http_analyzer)")
def agent(task: str, tools: tuple):
    """Execute agent task with tool use."""
    try:
        click.echo(f"{Fore.CYAN}Starting agent for: {task}{Style.RESET_ALL}")
        
        response = requests.post(
            f"{API_URL}/v1/agent",
            headers=get_headers(),
            json={
                "task": task,
                "available_tools": list(tools) if tools else None
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            
            click.echo(f"\n{Fore.GREEN}Agent Result:{Style.RESET_ALL}")
            click.echo(data.get("result", "No result"))
            
            if data.get("state"):
                state = data["state"]
                click.echo(f"\n{Fore.CYAN}Execution Details:{Style.RESET_ALL}")
                click.echo(f"  Iterations: {data.get('iterations')}")
                click.echo(f"  Status: {state.get('status')}")
                if state.get('tool_used'):
                    click.echo(f"  Tool Used: {state['tool_used']}")
            
            if data.get("local_inference"):
                click.echo(f"\n{Fore.CYAN}[Local inference via {data.get('inference_engine', 'unknown')}]{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.RED}Error: {response.status_code} - {response.text}{Style.RESET_ALL}")
    
    except requests.exceptions.Timeout:
        click.echo(f"{Fore.RED}Agent execution timed out{Style.RESET_ALL}")
    except requests.exceptions.ConnectionError:
        click.echo(f"{Fore.RED}Cannot connect to Tyla-Gen at {API_URL}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
def models():
    """List available models."""
    try:
        click.echo(f"{Fore.CYAN}Fetching available models...{Style.RESET_ALL}")
        
        response = requests.get(
            f"{API_URL}/v1/models",
            headers=get_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            click.echo(f"\n{Fore.CYAN}Current Model:{Style.RESET_ALL}")
            click.echo(f"  {data.get('current_model', 'None')} (Loaded: {'Yes' if data.get('model_loaded') else 'No'})")
            
            if data.get('available_models'):
                click.echo(f"\n{Fore.CYAN}Available Models:{Style.RESET_ALL}")
                
                table_data = []
                for model in data['available_models']:
                    table_data.append([
                        model['name'],
                        f"{model['size_gb']}GB",
                        model['quantization']
                    ])
                
                click.echo(tabulate(
                    table_data,
                    headers=["Name", "Size", "Quantization"],
                    tablefmt="grid"
                ))
        else:
            click.echo(f"{Fore.RED}Error: {response.status_code}{Style.RESET_ALL}")
    
    except requests.exceptions.ConnectionError:
        click.echo(f"{Fore.RED}Cannot connect to Tyla-Gen at {API_URL}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


@cli.command()
def rag():
    """List knowledge base documents."""
    try:
        click.echo(f"{Fore.CYAN}Fetching knowledge base...{Style.RESET_ALL}")
        
        response = requests.get(
            f"{API_URL}/v1/rag/documents",
            headers=get_headers(),
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            docs = data.get('documents', [])
            
            if docs:
                click.echo(f"\n{Fore.CYAN}Knowledge Base Documents ({len(docs)}):{Style.RESET_ALL}")
                
                table_data = []
                for doc in docs:
                    table_data.append([
                        doc['filename'],
                        doc['type'],
                        f"{doc['size']} bytes"
                    ])
                
                click.echo(tabulate(
                    table_data,
                    headers=["Filename", "Type", "Size"],
                    tablefmt="grid"
                ))
            else:
                click.echo(f"{Fore.YELLOW}No documents in knowledge base{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.RED}Error: {response.status_code}{Style.RESET_ALL}")
    
    except requests.exceptions.ConnectionError:
        click.echo(f"{Fore.RED}Cannot connect to Tyla-Gen at {API_URL}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")


if __name__ == "__main__":
    cli()
